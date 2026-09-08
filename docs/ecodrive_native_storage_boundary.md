# Bounded EcoDrive native storage follow-up

**PROVED static evidence:** the common Kona EcoDrive client references bus
`com.harman.service.EcoDrive` and object `/com/harman/service/EcoDrive`.
That concrete reference led to the named native `EcoDriveSvc` executable.
This follow-up examines that service only; Performance Pages does not delegate
its timer export to it. See the [consumer graph](removable_media_consumer_graph.md).

Source: `primary_iso/usr/share/MMC_IFS_EXTENSION/bin/EcoDriveSvc`, 2,733,845 bytes,
SHA-256 `9877299e99772a0ec7a03988bd7521abd8b2c9ceac499c820d3722392d15246e`.
Function identities below come from retained ELF symbols, not invented names.
The [native evidence report](../reports/kim19_runtime_analysis/performance_pages_native_storage.json)
binds eight complete function bodies by address, size and SHA-256, six selected
non-sensitive literals and fifteen decoded instruction windows. The full
functions were reviewed locally; no full disassembly or executable is committed.

## Fixed data source and device-specific destination

**PROVED:** `EcoDriveCore::startUSBTransfer(std::string&)` at `0x12d768`
sets the currently open data file on its USB handler, then distinguishes the
literal `All`/`all` choices from a single supplied filename. The all-files branch
calls `EcoDriveUSBHandler::transferFiles` at `0x12d8ec`; the single-file branch
calls `transferSingleFile` at `0x12d928`. Both receive
`EcoDriveTypes::DIR_FLASH_DATA`, the string object at `0x231658`.

Its initialization is independently bound: the initializer establishes global
base `0x2311d8` at `0x17c3dc..0x17c3e0`, adds `0x480` at `0x17c9c4`, and
constructs the string at `0x17c9d4` from literal address `0x20d8a4`:
`/fs/etfs/usr/var/ecoDrive/data`.

**PROVED:** `transferSingleFile` passes its data-directory and filename
arguments onward to `EcoDriveUSBHandler::transferFile` at `0x182b60`.
`transferFile`, at `0x1813fc`, obtains the inserted-device path through
`EcoDriveUSBInsertDetection::getPathToInsertedUSBDevice` at `0x181430`.
The latter reaches `EcoDriveUSBController::getInsertedUSB` at `0x17f060`.
This is a discovered service value; no fixed USB mount root is inferred here.

At `0x1817e8` and `0x1818a8`, the Uconnect/iFiat flags select which packaged
suffix to concatenate with the discovered device path:

| Selected constant | String-object address | Literal | Initialization |
|---|---|---|---|
| `USB_PATH_TO_ECODRIVE_DATA_UCONNECT` | `0x2318f8` | `/Uconnect/ecodrive/data` | `0x17cd7c..0x17cd8c`, literal `0x20daa4` |
| `USB_PATH_TO_ECODRIVE_DATA_IFIAT` | `0x2318dc` | `/iFiat/ecodrive/data` | `0x17cd54..0x17cd68`, literal `0x20da8c` |

**UNKNOWN:** this does not establish target service activation, the currently
inserted device path, flag values, caller authorization, or an ordinary KIM19 UI
that invokes the service. In particular it does not equate an EcoDrive device
path with Performance Pages' literal `/fs/usb0/`.

## Copy and free-space behavior

**PROVED:** `transferFile` calls `EcoDriveStorageManager::freeSpaceOnUSB`
at `0x181608`. The helper at `0x173850` calls `statvfs64` at `0x17385c` and
computes a shifted block-count product from the returned structure. The helper
does not branch on the `statvfs64` return value before using the structure.
This proves a free-space query in EcoDrive, not its reliability on a failed
query, and not a corresponding check in Performance Pages.

**PROVED:** `transferFile` passes source directory, selected destination
directory and filename to `EcoDriveStorageManager::moveFile` at `0x181a80`.
That routine uses the fixed `/tmp.tmp` intermediate suffix and invokes
`copyFile` at `0x173e50`, followed by existence, remove and rename branches.
The selected rename calls are at `0x173fdc` and `0x17401c`.
`copyFile` at `0x173a0c` invokes native `open` at `0x173a34`/`0x173a54`,
`write` at `0x173a88`, and `read` at `0x173a98`. The report preserves these
instructions; it does not simulate files or exercise any service operation.

**INFERRED scope assessment:** this is a more elaborate existing storage
facility than the timer writer, but the recovered core call path supplies a
fixed EcoDrive source directory and EcoDrive-specific USB destination suffix.
Its string filename parameter alone does not establish an ordinary generic
file-transfer capability. No path manipulation, payload construction, target
call, or export was attempted.

**UNKNOWN:** no producer-to-consumer relationship joins the Performance Pages
`timersResult` directory to EcoDrive's internal data directory. No KIM19 caller
of the common EcoDrive API was found in the focused census. These missing
edges prevent promoting the API to a proved timer-file handoff or a capability
available through ordinary resident application behavior.

## Reproduce

```powershell
python -m analysis_tools.performance_pages_native_storage --corpus $corpusWork
python -m analysis_tools.performance_pages_native_storage --corpus $corpusWork --check
python -m unittest analysis_tools.tests.test_performance_pages_native_storage
```

The generator rejects a different complete source hash, rechecks source bytes
after extraction, emits only allowlisted literals, rejects undecoded ARM
windows and refuses output under the recovered corpus. `--check` does not write.
