# Uconnect Network Probe

This directory contains an independently authored, host-tested TCP probe for
the RA4 resident Xlet environment. It is intentionally small: one worker owns
one listening socket and serves one client at a time. The Xlet UI receives
bounded status callbacks only through the LWUIT serial queue.

The generated artifact is always labeled:

```text
HOST-BUILT / UNSIGNED / NOT INSTALLABLE ON TARGET
```

It contains no installer, signer, certificate, target credential, native code,
vehicle API, CAN, diagnostic, persistence, autostart or firmware behavior.

## Protocol

- Listen on TCP port 8888 by default; host tests use an ephemeral port.
- Accept 1 to 256 printable ASCII payload bytes followed by LF.
- Accept CRLF by removing the one CR immediately before LF.
- Reply to a valid line with exactly `HELLO FROM UCONNECT\n`.
- Reply to an overlong line with `ERROR MESSAGE TOO LONG\n`, then close it.
- Reject empty and non-printable input with a bounded error, then close it.
- Use a fixed 257-byte buffer with bounded CRLF lookahead and serve later
  clients sequentially.

## Build

Requirements are Python 3, PowerShell and the pinned Eclipse Temurin JDK 8u504
described in `toolchain.json`.

```powershell
$Python = "C:\path\to\python.exe"
$JdkHome = "C:\Program Files\Eclipse Adoptium\jdk-8.0.504.1-hotspot"
& $Python -m unittest discover -s prototype/network_probe/tests -v
& prototype/network_probe/build.ps1 -JdkHome $JdkHome -Python $Python
```

Generated files are confined to ignored `prototype/network_probe/build/`.
The build packages only the three application types and the four anonymous UI
callback classes. It separately compiles, but does not package, the host
harness and compile-only Xlet/LWUIT declarations.

The validation gate checks deterministic JAR bytes, classfile major 48, an
exact Java API member allowlist, required networking/lifecycle calls, absence
of compile stubs and vendor runtime classes, and absence of native/JNI/USB/
vehicle/AppManager references. This is stricter than checking the classfile
version alone.

## Host Client

After starting `NetworkProbeHost` from the separately compiled host and
application class directories, send one line with:

```powershell
& $Python prototype/network_probe/network_probe_client.py 127.0.0.1 $Port "HELLO FROM PHONE"
```

Expected stdout is `HELLO FROM UCONNECT`; timeout, refusal, non-ASCII input and
input over 256 bytes return nonzero without a traceback.

## Evidence Boundary

Host tests prove the original server implementation's localhost protocol,
bounded shutdown behavior, lifecycle handoff and artifact properties. They do
not prove that the Xlet executes on RA4, receives networking permission, binds
a target socket, sees a usable interface, crosses a firewall, is reachable
through hotspot/Wi-Fi routing, or is unconstrained by AMS/application policy.

See `../../docs/network_probe_xlet.md` for measured results and the separately
authorized target experiment. Do not use generated output as an installable
package.
