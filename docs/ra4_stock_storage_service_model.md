# RA4 stock storage service model

Research date: 2026-09-08. This report separates the Performance Pages direct writer from adjacent stock storage services recovered in the KIM19 common base.

## Result

**PROVED:** Performance Pages does not cross a stock storage-service boundary for USB or SD export. Its chain is `TimerSaveOptionsEnum` -> fixed property path -> `java.io.File` -> `FileOutputStream`/`OutputStreamWriter`. No call to Kona FileIO, EcoDrive, AppManager storage access, or another IPC service appears in the selected writer path.

This matters operationally: the application inherits whatever mount namespace and Java policy the platform supplies. It does not receive the explicit MMC1 access coordination of Kona FileIO or the USB-status protocol of EcoDrive. Those neighboring facilities cannot be assumed to repair, authorize, or monitor the direct write.

## Boundary map

| Boundary | Role | Address/storage | Recovered semantics | Performance link |
|---|---|---|---|---|
| Performance direct writer | Writer/exporter | `/fs/usb0/timersResult`, `/mnt/sd0/timersResult` | Root existence check, child mkdir, exclusive file create, UTF8 writer | Complete static chain **PROVED** |
| Kona FileIO | Reader/writer/enumerator service | Application/MMC1 storage via `com.harman.fileio` | Permission checks, start/stop write session, `PlatformService.changeMMC1Mode("w"/"r")` | Timer link **UNKNOWN**; no syntactic caller/path edge found |
| EcoDrive Java service | Uploader/exporter/enumerator service | bus `com.harman.service.EcoDrive`, object `/com/harman/service/EcoDrive` | USB state/listeners, data listing/retrieval, `startUSBTransfer(fileName)` | Timer link **UNKNOWN**; no Performance/KIM caller found |
| Native EcoDriveSvc | Writer/exporter | flash source `/fs/etfs/usr/var/ecoDrive/data`, service-selected USB EcoDrive destinations | Transfers all data or a named data file, checks inserted USB/free space, moves into EcoDrive destination | Data-specific adjacent exporter; timer link **UNKNOWN** |
| DRMSync direct/helper I/O | Reader/writer | `/fs/mmc1/download/...` | Internal downloaded/provisioning file read/write | Separate app/internal workflow |

## Performance direct writer

`TimerSavingData.isDeviceAvailable(String)Z` reduces destination availability to `new File(root).exists()`. The application does not call a mount broker, check a service status, inspect free space, or subscribe to insertion/removal. It then creates `timersResult`, uses `createNewFile`, and writes the string.

**PROVED:** checked open/write failures map to stock status integers; an existing file skips the writer and is still reported as success. **UNKNOWN:** Java security policy, mount flags, and removal behavior on a live RA4. These gates sit below the recovered application boundary.

## Kona FileIO managed storage

**PROVED:** `kona.fileio.FileIOManager.getInstance()` returns `com.harman.fileio.FileIOManagerImpl` (class SHA-256 `4054b5dbb1a2051c382d4be1df16c7d0120ff9d7f5ae4a8c437c2302e47779aa`). `FileImpl` (SHA-256 `31e0631d34d4899b9565862853bd376141e1e105592734f464240647903199ad`) checks `com.harman.fileio.FileIOPermission` before read/write operations. `FileIOManagerImpl.startFileIoOperations()Z` calls `getWriteAccess()V` at BCI 8; `getWriteAccess()V` calls `PlatformService.changeMMC1Mode(String)Z` with `"w"` at BCI 37. `stopFileIoOperations()V` reaches `makeMMC1ReadOnly()V` at BCI 18, with a second exception-path call at BCI 25.

This service is evidence that RA4 has a managed internal file boundary. It does not establish that arbitrary app paths, USB, or SD are available through the same permission. No selected KIM19 call links Performance Pages to it.

## EcoDrive USB service

**PROVED:** `com.harman.ecodrive.EcoDriveImpl.startUSBTransfer(Ljava/lang/String;)Z` (109 instructions) uses the `fileName` map key literal at BCI 20, the operation literal `startUSBTransfer` at BCI 65, and calls `SvcIpcClient.invoke(Ljava/lang/String;Ljava/lang/Object;)Ljava/lang/Object;` at BCI 68; it treats an OK result as success. `getListOfDataFiles()[Lkona/ecoDrive/FileInformation;` calls the same IPC method at BCI 35 and decodes `numberOfFiles`, `files`, `name`, and `size`. The API separately exposes USB device/transfer/full status and data-file retrieval. `EcoDriveService` has class SHA-256 `dad4ce01544b6f20a8922b7882eefaf1e9593eaeb4e20e9847fd00def641808d`; `EcoDriveImpl` is `1b3ffe94353c1b02c93f4bcc99ea8804286419b1ee744d8dd72d75c30ebb5a14`.

**PROVED:** the [bounded native follow-up](ecodrive_native_storage_boundary.md) identified `EcoDriveSvc`, SHA-256 `9877299e99772a0ec7a03988bd7521abd8b2c9ceac499c820d3722392d15246e`. `Core::startUSBTransfer` dispatches `All`/`all` to `USBHandler::transferFiles` and other names to `USBHandler::transferSingleFile`; both receive `EcoDriveTypes::DIR_FLASH_DATA`, initialized from `/fs/etfs/usr/var/ecoDrive/data`. The transfer obtains the inserted USB path, checks free space, selects `/Uconnect/ecodrive/data` or `/iFiat/ecodrive/data`, and uses a `/tmp.tmp` intermediate in its copy/rename flow. Exact function addresses, body hashes, literals, and selected instructions are preserved in the [native evidence JSON](../reports/kim19_runtime_analysis/performance_pages_native_storage.json).

The recovered service is therefore data-specific. There is no proved interface in this trace that accepts `/fs/usb0/timersResult/<name>.html` as an input, and no Performance call to `startUSBTransfer`. Treating EcoDrive as a timer-file handoff would exceed the evidence.

## Stock write/read handoffs

| Handoff | Write side | Read side | End-to-end conclusion |
|---|---|---|---|
| Performance -> removable file -> external computer | Static writer **PROVED** | Outside corpus | **TARGET OBSERVATION REQUIRED** |
| Performance -> removable file -> any KIM19 app | Static writer **PROVED** | No path/discovery/format edge found | **UNKNOWN** in scoped corpus |
| DRMSync request -> internal MMC1 file -> DRMSync reader | Concrete methods and fixed path **PROVED** | Concrete readers **PROVED** for named internal files | Static internal handoff **PROVED**; runtime state unknown |
| EcoDrive flash data -> EcoDriveSvc -> USB | Java/native service semantics **PROVED** | Off-unit or later reader outside this trace | Runtime completion **TARGET OBSERVATION REQUIRED** |
| Kona FileIO client -> managed MMC1 storage | Service capability **PROVED** | Depends on a caller and permissions | Timer handoff **UNKNOWN**; no Performance client found |

## Security and reliability implications

- **PROVED:** direct Performance output does not invoke Kona FileIO's explicit `FileIOPermission` calls. The effective Java policy remains a separate **UNKNOWN** boundary; this call-path result does not imply an authorization bypass.
- **PROVED:** EcoDrive has insertion/free-space and status concepts that the Performance direct writer lacks. No code edge delegates those checks to EcoDrive on behalf of Performance Pages.
- **INFERRED:** direct application I/O is more exposed to removal races and ambiguous persistence because the writer has no service acknowledgment or atomic replacement. Actual QNX filesystem behavior remains target-dependent.
- **UNKNOWN:** whether the target grants the correct Performance package direct write permission and mounts the roots writable in the application's namespace.

## Evidence boundary

The Java conclusion comes from every class in 19 KIM19 and four common-base JARs. The canonical [consumer census](../reports/kim19_runtime_analysis/performance_pages_consumer_census.json) records the archive hashes, 7,384 class entries, zero parse errors, allowlisted literal-substring evidence, and selected syntactic invocations. Native follow-up was limited to the exact service named by the Java EcoDrive API. No global firmware absence claim is made. Static references establish implemented code and dataflow; service startup, package grants, media insertion, write success, and durable output remain **TARGET OBSERVATION REQUIRED**.
