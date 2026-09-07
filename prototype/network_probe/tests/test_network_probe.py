import importlib.util
import json
import os
import shutil
import socket
import subprocess
import tempfile
import threading
import time
import unittest
import zipfile
from pathlib import Path

from prototype.hello_uconnect.tests.test_artifact_tools import _minimal_class
from prototype.hello_uconnect.tools.artifact_tools import (
    ValidationError,
    audit_artifact,
)


REPO_ROOT = Path(__file__).resolve().parents[3]
PROJECT_ROOT = REPO_ROOT / "prototype" / "network_probe"
MAIN_CLASS = "com.jfhutchi.uconnect.networkprobe.NetworkProbeHost"
BUILD_TEMP = None
COMPILED_CLASSES = None


def _jdk_tool(name):
    configured = os.environ.get("NETWORK_PROBE_JDK_HOME")
    candidates = []
    if configured:
        candidates.append(Path(configured))
    candidates.append(
        REPO_ROOT
        / "analysis_work"
        / "toolchains"
        / "temurin8u504"
        / "jdk8u504-b01"
    )
    candidates.append(
        REPO_ROOT.parent
        / "jeep_uconnect_custom"
        / "analysis_work"
        / "toolchains"
        / "temurin8u504"
        / "jdk8u504-b01"
    )
    executable = name + (".exe" if os.name == "nt" else "")
    for candidate in candidates:
        tool = candidate / "bin" / executable
        if tool.is_file():
            return tool
    raise RuntimeError("Temurin JDK 8 is required; set NETWORK_PROBE_JDK_HOME")


def _load_client_module():
    path = PROJECT_ROOT / "network_probe_client.py"
    spec = importlib.util.spec_from_file_location("network_probe_client", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _read_reply(sock):
    reply = bytearray()
    while len(reply) <= 128:
        chunk = sock.recv(1)
        if not chunk:
            break
        reply.extend(chunk)
        if chunk == b"\n":
            break
    return bytes(reply)


def _raw_exchange(port, payload):
    with socket.create_connection(("127.0.0.1", port), timeout=2.0) as client:
        client.settimeout(2.0)
        client.sendall(payload)
        return _read_reply(client)


def setUpModule():
    global BUILD_TEMP, COMPILED_CLASSES
    BUILD_TEMP = tempfile.TemporaryDirectory()
    COMPILED_CLASSES = Path(BUILD_TEMP.name) / "classes"
    COMPILED_CLASSES.mkdir()
    sources = [
        PROJECT_ROOT
        / "src/com/jfhutchi/uconnect/networkprobe/NetworkProbeListener.java",
        PROJECT_ROOT
        / "src/com/jfhutchi/uconnect/networkprobe/NetworkProbeServer.java",
        PROJECT_ROOT
        / "host_src/com/jfhutchi/uconnect/networkprobe/NetworkProbeHost.java",
    ]
    subprocess.run(
        [
            str(_jdk_tool("javac")),
            "-source",
            "1.4",
            "-target",
            "1.4",
            "-encoding",
            "US-ASCII",
            "-d",
            str(COMPILED_CLASSES),
        ]
        + [str(path) for path in sources],
        check=True,
        capture_output=True,
        text=True,
    )


def tearDownModule():
    if BUILD_TEMP is not None:
        BUILD_TEMP.cleanup()


class _HostProcess:
    def __init__(self, classes):
        self.process = subprocess.Popen(
            [str(_jdk_tool("java")), "-cp", str(classes), MAIN_CLASS, "0"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        first_line = self.process.stdout.readline().strip()
        if not first_line.startswith("PORT "):
            _stdout, stderr = self.process.communicate(timeout=3)
            raise AssertionError(
                "host did not publish a port: %r stderr=%r"
                % (first_line, stderr)
            )
        self.port = int(first_line.split()[1])

    def stop(self):
        if self.process.poll() is None:
            self.process.stdin.write("STOP\n")
            self.process.stdin.flush()
        stdout, stderr = self.process.communicate(timeout=3)
        if self.process.returncode != 0:
            raise AssertionError(
                "host exit=%d stdout=%r stderr=%r"
                % (self.process.returncode, stdout, stderr)
            )
        if "Exception" in stderr or "at " in stderr:
            raise AssertionError("host emitted a stack trace: %s" % stderr)

    def terminate(self):
        if self is not None and self.process.poll() is None:
            self.process.kill()
            self.process.communicate(timeout=3)


class NetworkProbeProtocolTests(unittest.TestCase):
    def setUp(self):
        self.host = _HostProcess(COMPILED_CLASSES)

    def tearDown(self):
        if self.host is not None:
            self.host.terminate()

    def _stop_cleanly(self):
        self.host.stop()
        self.host = None

    def test_lf_round_trip(self):
        self.assertEqual(
            _raw_exchange(self.host.port, b"HELLO FROM PHONE\n"),
            b"HELLO FROM UCONNECT\n",
        )

    def test_crlf_round_trip(self):
        self.assertEqual(
            _raw_exchange(self.host.port, b"HELLO FROM PHONE\r\n"),
            b"HELLO FROM UCONNECT\n",
        )

    def test_exactly_256_payload_bytes_are_accepted(self):
        self.assertEqual(
            _raw_exchange(self.host.port, b"A" * 256 + b"\n"),
            b"HELLO FROM UCONNECT\n",
        )
        self.assertEqual(
            _raw_exchange(self.host.port, b"A" * 256 + b"\r\n"),
            b"HELLO FROM UCONNECT\n",
        )

    def test_overlong_input_is_rejected_and_closed(self):
        self.assertEqual(
            _raw_exchange(self.host.port, b"A" * 257 + b"\n"),
            b"ERROR MESSAGE TOO LONG\n",
        )

    def test_empty_and_control_input_are_rejected(self):
        self.assertEqual(
            _raw_exchange(self.host.port, b"\n"), b"ERROR EMPTY MESSAGE\n"
        )
        self.assertEqual(
            _raw_exchange(self.host.port, b"BAD\x01BYTE\n"),
            b"ERROR INVALID MESSAGE\n",
        )

    def test_non_ascii_input_is_rejected(self):
        self.assertEqual(
            _raw_exchange(self.host.port, b"BAD\xffBYTE\n"),
            b"ERROR INVALID MESSAGE\n",
        )

    def test_multiple_clients_are_served_sequentially(self):
        for message in (b"FIRST\n", b"SECOND\n"):
            self.assertEqual(
                _raw_exchange(self.host.port, message),
                b"HELLO FROM UCONNECT\n",
            )

    def test_incomplete_disconnect_does_not_stop_server(self):
        client = socket.create_connection(("127.0.0.1", self.host.port), timeout=2)
        client.sendall(b"INCOMPLETE")
        client.close()
        self.assertEqual(
            _raw_exchange(self.host.port, b"COMPLETE\n"),
            b"HELLO FROM UCONNECT\n",
        )

    def test_stop_releases_blocked_accept_and_is_idempotent(self):
        self._stop_cleanly()

    def test_stop_releases_blocked_client_read(self):
        client = socket.create_connection(("127.0.0.1", self.host.port), timeout=2)
        try:
            self._stop_cleanly()
        finally:
            client.close()


class NetworkProbeArtifactTests(unittest.TestCase):
    def _run_build(self):
        shell = shutil.which("pwsh") or shutil.which("powershell")
        if shell is None:
            self.fail("PowerShell is required for the network-probe build")
        result = subprocess.run(
            [
                shell,
                "-NoProfile",
                "-File",
                str(PROJECT_ROOT / "build.ps1"),
                "-JdkHome",
                str(_jdk_tool("javac").parent.parent),
                "-Python",
                os.sys.executable,
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_build_is_deterministic_major_48_and_application_only(self):
        self._run_build()
        output = PROJECT_ROOT / "build" / "out"
        jar_path = output / "network-probe-xlet.jar"
        first_bytes = jar_path.read_bytes()
        bytecode = json.loads(
            (output / "bytecode-report.json").read_text(encoding="ascii")
        )["bytecode"]
        dependencies = json.loads(
            (output / "dependency-report.json").read_text(encoding="ascii")
        )["dependencies"]
        with zipfile.ZipFile(jar_path) as archive:
            members = archive.namelist()

        expected_members = {
            "com/jfhutchi/uconnect/networkprobe/NetworkProbeListener.class",
            "com/jfhutchi/uconnect/networkprobe/NetworkProbeServer.class",
            "com/jfhutchi/uconnect/networkprobe/NetworkProbeXlet.class",
            "com/jfhutchi/uconnect/networkprobe/NetworkProbeXlet$1.class",
            "com/jfhutchi/uconnect/networkprobe/NetworkProbeXlet$2.class",
            "com/jfhutchi/uconnect/networkprobe/NetworkProbeXlet$3.class",
            "com/jfhutchi/uconnect/networkprobe/NetworkProbeXlet$4.class",
        }
        self.assertEqual(set(members), expected_members)
        self.assertFalse(any("NetworkProbeHost" in name for name in members))
        self.assertFalse(any(name.startswith("com/sun/lwuit/") for name in members))
        self.assertFalse(
            any(name.startswith("javax/microedition/xlet/") for name in members)
        )
        self.assertEqual(bytecode["application_classfile_majors"], [48])
        self.assertEqual(bytecode["native_methods"], 0)
        self.assertEqual(bytecode["invokedynamic_references"], 0)
        self.assertEqual(dependencies["bundled_compile_stubs"], 0)
        self.assertEqual(dependencies["bundled_vendor_runtime_classes"], 0)
        self.assertEqual(dependencies["custom_native_libraries"], 0)
        self.assertEqual(dependencies["jni_references"], 0)
        self.assertEqual(dependencies["usb_references"], 0)
        self.assertEqual(dependencies["vehicle_service_references"], 0)
        self.assertEqual(dependencies["appmanager_privilege_references"], 0)
        self.assertGreater(
            dependencies["observed_api_references"]["networking"], 0
        )
        status = (output / "BUILD-STATUS.txt").read_text(encoding="ascii")
        self.assertIn("Application classfile major:        48", status)
        self.assertIn("Observed networking references:", status)
        self.assertNotIn("\nNetworking references:", status)
        self.assertIn("Artifact installability:            NO", status)

        self._run_build()
        self.assertEqual(jar_path.read_bytes(), first_bytes)

    def test_exact_api_policy_rejects_newer_java_member(self):
        synthetic = Path(tempfile.mkdtemp())
        try:
            jar_path = synthetic / "synthetic.jar"
            with zipfile.ZipFile(jar_path, "w") as archive:
                archive.writestr(
                    "com/jfhutchi/uconnect/networkprobe/NetworkProbeXlet.class",
                    _minimal_class(
                        class_name=(
                            "com/jfhutchi/uconnect/networkprobe/NetworkProbeXlet"
                        ),
                        method_refs=(
                            ("java/util/concurrent/Executor", "execute", "(Ljava/lang/Runnable;)V"),
                        ),
                    ),
                )
            with self.assertRaisesRegex(ValidationError, "unexpected API"):
                audit_artifact(
                    jar_path,
                    PROJECT_ROOT / "descriptor" / "xlet.properties",
                    PROJECT_ROOT / "api-allowlist.json",
                )
        finally:
            shutil.rmtree(synthetic)


class NetworkProbeClientTests(unittest.TestCase):
    def test_client_exchanges_one_message(self):
        host = _HostProcess(COMPILED_CLASSES)
        try:
            client = _load_client_module()
            self.assertEqual(
                client.exchange("127.0.0.1", host.port, "HELLO FROM PHONE", 2),
                "HELLO FROM UCONNECT",
            )
        finally:
            host.stop()

    def test_client_rejects_non_ascii_and_overlong_messages(self):
        client = _load_client_module()
        for message in ("SNOWMAN \N{SNOWMAN}", "A" * 257):
            with self.subTest(message=message[:16]):
                with self.assertRaises(client.ProbeClientError):
                    client.exchange("127.0.0.1", 9, message, 0.1)

    def test_client_reports_timeout_without_traceback(self):
        listener = socket.socket()
        listener.bind(("127.0.0.1", 0))
        listener.listen(1)

        def accept_without_reply():
            connection, _address = listener.accept()
            try:
                time.sleep(0.3)
            finally:
                connection.close()
                listener.close()

        worker = threading.Thread(target=accept_without_reply)
        worker.start()
        try:
            client = _load_client_module()
            with self.assertRaisesRegex(client.ProbeClientError, "timed out"):
                client.exchange("127.0.0.1", listener.getsockname()[1], "HELLO", 0.05)
        finally:
            worker.join(2)

    def test_client_cli_reports_connection_refusal_without_traceback(self):
        listener = socket.socket()
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
        listener.close()
        result = subprocess.run(
            [
                os.fspath(Path(os.sys.executable)),
                os.fspath(PROJECT_ROOT / "network_probe_client.py"),
                "127.0.0.1",
                str(port),
                "HELLO",
            ],
            capture_output=True,
            text=True,
            timeout=3,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("connection failed", result.stderr.lower())
        self.assertNotIn("Traceback", result.stderr)


class NetworkProbeLifecycleTests(unittest.TestCase):
    def test_lifecycle_ui_queue_and_destroy_races(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            classes = Path(temp_dir) / "classes"
            classes.mkdir()
            sources = sorted(
                PROJECT_ROOT.joinpath("test_support", "src").rglob("*.java")
            ) + sorted(PROJECT_ROOT.joinpath("src").rglob("*.java"))
            compile_result = subprocess.run(
                [
                    str(_jdk_tool("javac")),
                    "-source",
                    "1.4",
                    "-target",
                    "1.4",
                    "-encoding",
                    "US-ASCII",
                    "-d",
                    str(classes),
                ]
                + [str(path) for path in sources],
                capture_output=True,
                text=True,
            )
            self.assertEqual(compile_result.returncode, 0, compile_result.stderr)
            result = subprocess.run(
                [
                    str(_jdk_tool("java")),
                    "-cp",
                    str(classes),
                    "com.jfhutchi.uconnect.networkprobe.NetworkProbeLifecycleTest",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), "LIFECYCLE OK")
            self.assertNotIn("Exception", result.stderr)


if __name__ == "__main__":
    unittest.main()
