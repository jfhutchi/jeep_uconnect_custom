import hashlib
import json
import struct
import tempfile
import unittest
import zipfile
from pathlib import Path

from prototype.hello_uconnect.tools.artifact_tools import (
    ValidationError,
    audit_artifact,
    validate_descriptor,
    write_deterministic_jar,
)
from prototype.hello_uconnect.tools.build_installed_layout_skeleton import (
    build_installed_layout_skeleton,
)


def _u1(value):
    return struct.pack(">B", value)


def _u2(value):
    return struct.pack(">H", value)


def _u4(value):
    return struct.pack(">I", value)


class _ConstantPool:
    def __init__(self):
        self.entries = []

    def utf8(self, value):
        encoded = value.encode("utf-8")
        self.entries.append(_u1(1) + _u2(len(encoded)) + encoded)
        return len(self.entries)

    def class_(self, name):
        name_index = self.utf8(name)
        self.entries.append(_u1(7) + _u2(name_index))
        return len(self.entries)

    def name_and_type(self, name, descriptor):
        name_index = self.utf8(name)
        descriptor_index = self.utf8(descriptor)
        self.entries.append(_u1(12) + _u2(name_index) + _u2(descriptor_index))
        return len(self.entries)

    def methodref(self, owner, name, descriptor):
        owner_index = self.class_(owner)
        name_type_index = self.name_and_type(name, descriptor)
        self.entries.append(_u1(10) + _u2(owner_index) + _u2(name_type_index))
        return len(self.entries)

    def invokedynamic(self, name, descriptor):
        name_type_index = self.name_and_type(name, descriptor)
        self.entries.append(_u1(18) + _u2(0) + _u2(name_type_index))
        return len(self.entries)

    def serialize(self):
        return _u2(len(self.entries) + 1) + b"".join(self.entries)


def _minimal_class(
    class_name="com/jfhutchi/uconnect/hello/HelloUconnectXlet",
    major=48,
    method_refs=(),
    field_descriptors=(),
    native_method=False,
    invokedynamic=False,
):
    pool = _ConstantPool()
    this_class = pool.class_(class_name)
    super_class = pool.class_("java/lang/Object")
    for owner, name, descriptor in method_refs:
        pool.methodref(owner, name, descriptor)
    if invokedynamic:
        pool.invokedynamic("dynamicCall", "()V")

    fields = []
    for field_number, field_descriptor in enumerate(field_descriptors):
        field_name = pool.utf8("field%d" % field_number)
        descriptor_index = pool.utf8(field_descriptor)
        fields.append(
            _u2(0x0002)
            + _u2(field_name)
            + _u2(descriptor_index)
            + _u2(0)
        )

    methods = []
    if native_method:
        method_name = pool.utf8("nativeProbe")
        method_descriptor = pool.utf8("()V")
        methods.append(
            _u2(0x0101)
            + _u2(method_name)
            + _u2(method_descriptor)
            + _u2(0)
        )

    return (
        b"\xca\xfe\xba\xbe"
        + _u2(0)
        + _u2(major)
        + pool.serialize()
        + _u2(0x0021)
        + _u2(this_class)
        + _u2(super_class)
        + _u2(0)
        + _u2(len(fields))
        + b"".join(fields)
        + _u2(len(methods))
        + b"".join(methods)
        + _u2(0)
    )


class ArtifactToolsTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.policy_path = self.root / "api-allowlist.json"
        self.policy_path.write_text(
            json.dumps(
                {
                    "target_major": 48,
                    "application_prefix": "com/jfhutchi/uconnect/hello/",
                    "expected_main_class": (
                        "com.jfhutchi.uconnect.hello.HelloUconnectXlet"
                    ),
                    "expected_app_id": "4e9838d7-d08f-5f3a-be95-b309114fc22e",
                    "allowed_class_owners": ["java/lang/Object"],
                    "allowed_members": [],
                    "prohibited_owner_prefixes": {
                        "networking": ["java/net/", "javax/microedition/io/"],
                        "usb": ["com/harman/usb/", "javax/usb/"],
                        "vehicle_service": [
                            "com/harman/can/",
                            "com/harman/service/vehicle/",
                        ],
                        "appmanager_privilege": [
                            "com/harman/appmanager/",
                            "com/harman/kona/appmanager/",
                        ],
                    },
                    "prohibited_members": {
                        "jni": [
                            [
                                "java/lang/System",
                                "loadLibrary",
                                "(Ljava/lang/String;)V",
                            ],
                            [
                                "java/lang/System",
                                "load",
                                "(Ljava/lang/String;)V",
                            ],
                        ]
                    },
                },
                sort_keys=True,
            ),
            encoding="ascii",
        )
        self.descriptor_path = self.root / "xlet.properties"
        self._write_safe_descriptor()

    def tearDown(self):
        self.temp_dir.cleanup()

    def _write_safe_descriptor(self, overrides=None):
        values = {
            "xlet.appId": "4e9838d7-d08f-5f3a-be95-b309114fc22e",
            "xlet.mainClass": "com.jfhutchi.uconnect.hello.HelloUconnectXlet",
            "xlet.name": "Hello Uconnect",
            "xlet.vendor": "jfhutchi Jeep Uconnect Custom",
            "xlet.version": "0.1.0",
            "xlet.jarFile": "hello-uconnect.jar",
            "xlet.hasGUI": "true",
            "xlet.headless": "false",
            "xlet.isAudio": "false",
            "xlet.daemon": "false",
            "xlet.PauseAllowed": "false",
        }
        values.update(overrides or {})
        content = (
            "# HOST-BUILT / UNSIGNED / NOT INSTALLABLE ON TARGET\n"
            + "\n".join("%s=%s" % item for item in sorted(values.items()))
            + "\n"
        )
        self.descriptor_path.write_text(content, encoding="ascii")

    def _write_jar(
        self,
        class_bytes=None,
        extra_members=None,
        class_member="com/jfhutchi/uconnect/hello/HelloUconnectXlet.class",
    ):
        jar_path = self.root / "synthetic.jar"
        with zipfile.ZipFile(jar_path, "w", compression=zipfile.ZIP_STORED) as archive:
            if class_bytes is not None:
                archive.writestr(
                    class_member, class_bytes
                )
            for name, data in extra_members or []:
                archive.writestr(name, data)
        return jar_path

    def _audit(self, class_bytes=None, extra_members=None, class_member=None):
        return audit_artifact(
            self._write_jar(
                class_bytes,
                extra_members,
                class_member=(
                    class_member
                    or "com/jfhutchi/uconnect/hello/HelloUconnectXlet.class"
                ),
            ),
            self.descriptor_path,
            self.policy_path,
        )

    def test_accepts_minimal_major_48_application_class(self):
        report = self._audit(_minimal_class())
        self.assertEqual(report["bytecode"]["application_classfile_majors"], [48])
        self.assertEqual(report["bytecode"]["native_methods"], 0)
        self.assertEqual(report["dependencies"]["unexpected_api_references"], 0)

    def test_rejects_wrong_classfile_version(self):
        with self.assertRaisesRegex(ValidationError, "major.*49"):
            self._audit(_minimal_class(major=49))

    def test_rejects_missing_or_misplaced_descriptor_main_class(self):
        with self.assertRaisesRegex(ValidationError, "main class"):
            self._audit(
                _minimal_class(class_name="com/jfhutchi/uconnect/hello/Synthetic"),
                class_member="com/jfhutchi/uconnect/hello/Synthetic.class",
            )
        with self.assertRaisesRegex(ValidationError, "path does not match"):
            self._audit(
                _minimal_class(),
                class_member="com/jfhutchi/uconnect/hello/Misplaced.class",
            )

    def test_rejects_unexpected_constant_pool_member(self):
        class_bytes = _minimal_class(
            method_refs=(("java/lang/Object", "wait", "()V"),)
        )
        with self.assertRaisesRegex(ValidationError, "unexpected API member"):
            self._audit(class_bytes)

    def test_rejects_bundled_compile_stub(self):
        with self.assertRaisesRegex(ValidationError, "compile stub"):
            self._audit(
                _minimal_class(),
                (("javax/microedition/xlet/Xlet.class", _minimal_class()),),
            )

    def test_rejects_native_method_and_native_library(self):
        with self.assertRaisesRegex(ValidationError, "native method"):
            self._audit(_minimal_class(native_method=True))
        with self.assertRaisesRegex(ValidationError, "native library"):
            self._audit(_minimal_class(), (("lib/hello.so", b"not-an-elf"),))

    def test_rejects_invokedynamic(self):
        with self.assertRaisesRegex(ValidationError, "invokedynamic"):
            self._audit(_minimal_class(invokedynamic=True))

    def test_rejects_jni_load_reference(self):
        class_bytes = _minimal_class(
            method_refs=(
                ("java/lang/System", "loadLibrary", "(Ljava/lang/String;)V"),
            )
        )
        with self.assertRaisesRegex(ValidationError, "jni"):
            self._audit(class_bytes)

    def test_rejects_prohibited_owner_categories(self):
        cases = (
            ("networking", "java/net/Socket"),
            ("usb", "com/harman/usb/UsbManager"),
            ("vehicle_service", "com/harman/can/CanService"),
            ("appmanager_privilege", "com/harman/appmanager/AppManager"),
        )
        for category, owner in cases:
            with self.subTest(category=category):
                class_bytes = _minimal_class(method_refs=((owner, "open", "()V"),))
                with self.assertRaisesRegex(ValidationError, category):
                    self._audit(class_bytes)

    def test_rejects_prohibited_descriptor_only_type(self):
        class_bytes = _minimal_class(field_descriptors=("Ljava/net/Socket;",))
        with self.assertRaisesRegex(ValidationError, "networking"):
            self._audit(class_bytes)

    def test_deterministic_jar_inventory_and_hash(self):
        source = self.root / "classes"
        (source / "z").mkdir(parents=True)
        (source / "a").mkdir(parents=True)
        (source / "z" / "Second.class").write_bytes(_minimal_class())
        (source / "a" / "First.class").write_bytes(_minimal_class())
        first = self.root / "first.jar"
        second = self.root / "second.jar"

        inventory_first = write_deterministic_jar(source, first)
        inventory_second = write_deterministic_jar(source, second)

        self.assertEqual(inventory_first, ["a/First.class", "z/Second.class"])
        self.assertEqual(inventory_first, inventory_second)
        self.assertEqual(first.read_bytes(), second.read_bytes())
        self.assertEqual(
            hashlib.sha256(first.read_bytes()).hexdigest(),
            hashlib.sha256(second.read_bytes()).hexdigest(),
        )

    def test_descriptor_safety_fields(self):
        result = validate_descriptor(
            self.descriptor_path,
            expected_main_class="com.jfhutchi.uconnect.hello.HelloUconnectXlet",
            expected_app_id="4e9838d7-d08f-5f3a-be95-b309114fc22e",
        )
        self.assertFalse(result["autostart"])
        self.assertFalse(result["daemon"])
        self.assertFalse(result["audio_app"])
        self.assertFalse(result["installable"])

    def test_descriptor_rejects_autostart_daemon_audio_or_privilege_fields(self):
        unsafe_cases = (
            ("xlet.autostart", "true"),
            ("xlet.daemon", "true"),
            ("xlet.isAudio", "true"),
            ("xlet.appMgrPermission", "appMgr"),
            ("xlet.projectionPermission", "true"),
            ("xlet.vehicleServicePermission", "true"),
        )
        for key, value in unsafe_cases:
            with self.subTest(key=key):
                self._write_safe_descriptor({key: value})
                with self.assertRaises(ValidationError):
                    validate_descriptor(
                        self.descriptor_path,
                        expected_main_class=(
                            "com.jfhutchi.uconnect.hello.HelloUconnectXlet"
                        ),
                        expected_app_id="4e9838d7-d08f-5f3a-be95-b309114fc22e",
                    )

    def test_builds_deterministic_unsigned_installed_layout_skeleton(self):
        application_jar = self._write_jar(_minimal_class())
        output = self.root / "research-layout"

        first = build_installed_layout_skeleton(
            application_jar, self.descriptor_path, output
        )
        app_root = output / "4e9838d7-d08f-5f3a-be95-b309114fc22e"
        payload = app_root / "prog" / "jars" / "hello-uconnect.jar"
        self.assertEqual(payload.read_bytes(), application_jar.read_bytes())
        self.assertEqual(
            (app_root / "prog" / "xlet.properties").read_bytes(),
            self.descriptor_path.read_bytes(),
        )
        self.assertEqual(
            (app_root / "prog" / "jars" / "magic.txt").read_bytes(), b"HB_CMC"
        )
        self.assertFalse((app_root / "prog" / "jars" / "key.jar").exists())
        self.assertFalse(first["installable"])
        self.assertEqual(
            first["missing"],
            ["payload JAR root xlet.properties", "prog/jars/key.jar"],
        )
        self.assertIn(
            "UNSIGNED / NON-INSTALLABLE / RESEARCH ARTIFACT",
            (output / "RESEARCH-STATUS.txt").read_text(encoding="ascii"),
        )

    def test_skeleton_rejects_parent_directory_app_id(self):
        application_jar = self._write_jar(_minimal_class())
        self._write_safe_descriptor({"xlet.appId": ".."})

        with self.assertRaisesRegex(ValueError, "safe directory name"):
            build_installed_layout_skeleton(
                application_jar,
                self.descriptor_path,
                self.root / "research-layout",
            )

    def test_skeleton_rejects_windows_ads_jar_filename(self):
        application_jar = self._write_jar(_minimal_class())
        self._write_safe_descriptor({"xlet.jarFile": "foo:bar.jar"})

        with self.assertRaisesRegex(ValueError, "safe JAR filename"):
            build_installed_layout_skeleton(
                application_jar,
                self.descriptor_path,
                self.root / "research-layout",
            )


if __name__ == "__main__":
    unittest.main()
