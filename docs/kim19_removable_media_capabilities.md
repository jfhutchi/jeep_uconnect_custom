# KIM19 removable-media capabilities

Research date: 2026-09-08. Scope is all 19 JARs under KIM19 plus `ams_initializer.jar`, `kona.jar`, and the nearby development/production common security JARs. The corpus contains 7,384 class entries; the focused classfile scan completed with zero parse errors.

## Result

**PROVED:** the only concrete removable-media file write constructed by a KIM19 application in this scoped corpus is Performance Pages timer export. Other file surfaces are internal storage operations, uncalled helpers, or common-base services without a KIM19 caller. This is a bounded conclusion and not a claim about every binary in the firmware.

| Rank | Surface | Role | Storage and operation | Static reachability | Runtime status |
|---|---|---|---|---|---|
| 1 | Performance Pages Viper/Jeep/L-Series | Writer/exporter | Direct `.html` output to `/fs/usb0/timersResult` or `/mnt/sd0/timersResult` | Complete UI option -> path -> create -> writer chain **PROVED** | **TARGET OBSERVATION REQUIRED** |
| 2 | DRMSync | Reader/writer | Reads/writes fixed files and downloaded bytes under `/fs/mmc1/download` | Concrete request/manager chains **PROVED** | Internal/backend workflow; removable-media role **UNKNOWN** |
| 3 | Common EcoDrive API/service | Uploader/exporter/enumerator | Transfers EcoDrive data from `/fs/etfs/usr/var/ecoDrive/data` to service-selected USB destinations | Java service calls and native data-specific transfer **PROVED**; no KIM19 caller | KIM19 reachability **UNKNOWN** |
| 4 | Common Kona FileIO | Reader/writer/enumerator | Permission-gated generic file operations; switches MMC1 write/read mode | Service implementation **PROVED**; no KIM19 timer caller | KIM19 reachability **UNKNOWN** |
| 5 | Store Base64 file helpers | Reader/writer codec utility; importer/exporter role **UNKNOWN** | Generic file encode/decode streams | Utility **PROVED** present; only self-calls found | Entry-point reachability **UNKNOWN** |

## Performance Pages

The three packages are:

| Variant | JAR SHA-256 | Writer class SHA-256 |
|---|---|---|
| Viper 01.23.01 | `00b15a1d7268565c3644ba07e1fb1c3789f27b9b118029510652d03139d3ad0d` | `65fbddc04b2e39e32c03028b1294c1a6b98e7062b82ef2e3a73d049428d06d7d` |
| Jeep 01.57.01 | `bfcfe3fdc6bf978c36e6e50860458e1def531b09ca046725312a373cf935f566` | `65fbddc04b2e39e32c03028b1294c1a6b98e7062b82ef2e3a73d049428d06d7d` |
| MY15 L-Series 02.01.01 | `8a421cfda32d05f29d92e263d62307623a1603ec4e2d3c9183ca69b2ff33d4f6` | `d8cd498fc1cd7d9a2bcd622c3f11c0e754d4f2d9a19d73d15f3d0fe628be63c0` |

**PROVED:** Viper and Jeep writer/enum/factory class bytes are identical. L-Series differs in class bytes and resource naming but preserves the storage behavior. The application directly uses `java.io`; it does not delegate removable writes to Kona FileIO or EcoDrive.

**PROVED:** the preflight is only root `File.exists()`. There is no dynamic volume enumeration, writeability/free-space check, removal listener, atomic replacement, or collision overwrite. Existing output names are reported as success without rewriting. The exact target permission grant and actual persistence are **UNKNOWN** until observed.

## DRMSync comparison

**PROVED:** the DRMSync JAR SHA-256 is `721695df2518f1665c2658e156431f93d04e13739c51b149a10ea1494ef77225`. Its concrete file activity includes:

- `MTSSRTBrandDetailRequest.processJSONObject(Lorg/json/me/JSONObject;)V` reading `/fs/mmc1/download/isSRT` with `FileInputStream(File)` at BCI 35; `writeToBrandFile(Z)V` deletes at BCI 52, creates at BCI 57, opens at BCI 78, and writes at BCI 108 or 135.
- `MTSContentStreamRequest.processStream(Ljava/io/InputStream;)V` calling `HuDRMFileManager.saveBytesToFile(Ljava/io/InputStream;Ljava/io/File;)J` at BCI 198 for downloaded content under `/fs/mmc1/download`.
- `MTSGrantPayloadRequest.processStream(Ljava/io/InputStream;)V` calling the same save helper at BCI 77.
- `HuDeprovManager` reading/writing a fixed internal provisioning file after `AppManager.getDownloadFolderAccess()`.

These flows prove stock-signed file I/O but do not prove removable media. They use internal MMC1 paths and service/backend data. Sensitive values are unnecessary to the storage conclusion and are not reproduced here.

## Common-base service comparison

**PROVED:** `kona.jar` SHA-256 `19390472018f02d998690b982f00eb68da5d40d7a8d6fba91499677651015f92` contains two materially different storage interfaces:

- Kona FileIO enforces `FileIOPermission`, coordinates application write access, and changes MMC1 mode through `PlatformService`. It models managed internal application storage.
- EcoDrive exposes `startUSBTransfer`, USB status/listeners, file listing, and file retrieval over the `com.harman.service.EcoDrive` IPC boundary. [Bounded native evidence](ecodrive_native_storage_boundary.md) binds its source data to the EcoDrive directory and its destination to the discovered USB device plus an EcoDrive-specific suffix, so it is not a generic arbitrary-path copy service in the recovered flow.

**PROVED scoped negative:** no class in the 19 KIM19 JARs invokes either interface for a Performance timer file. Static API availability does not imply an application grant, service availability, or runtime call.

## Store helper comparison

**PROVED:** the Uconnect Store JAR SHA-256 is `2e5b3f7e1c7857950f7ea536b3975f1feebff744a47fb141551bbb6c23c7d552`. Its Base64 class has public file methods, but exhaustive calls within the scoped 23 archives identify only self-calls in that class and no destination constants or file chooser/discovery path. Runtime use of those file entry points and timer-file consumption are **UNKNOWN**.

## Coverage and stopping boundary

All 19 KIM19 archive identities, including key/resource-only JARs, were hashed and included. Four common-base archives were scanned alongside them. The reproducible [consumer census](../reports/kim19_runtime_analysis/performance_pages_consumer_census.json) records all 23 hashes, 7,384 class entries, zero parse errors, allowlisted storage/format literal-substring evidence, and selected invocation metadata. The search followed concrete file/path/service references into the adjacent Kona implementations and the exact EcoDrive native service; it did not broaden into a whole-firmware string search.

The static stopping point is defensible: Performance Pages has the only closed KIM19 removable-write construction, and each plausible consumer/service candidate stops at a named missing call, path, discovery, format, or runtime gate. The result does not change the separately selected target observation action.
