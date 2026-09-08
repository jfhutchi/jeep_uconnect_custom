# Performance Pages storage model

Research date: 2026-09-08. This report is a static model of the three Performance Pages packages in the recovered RA4 18.45.01 KIM19 corpus. It does not assert that a package is installed, visible, authorized, launched, or granted write access on a particular radio.

## Result

**PROVED:** Viper, Jeep, and L-Series Performance Pages implement the same removable-media export shape. The selected save option supplies a fixed root, `TimerSavingData` tests only whether that root exists, creates a `timersResult` child, constructs `<caller basename>.html`, and writes the caller-supplied HTML with an `OutputStreamWriter` using `UTF8`.

| UI option | Bundled root | Effective directory | Selection source |
|---|---|---|---|
| USB | `/fs/usb0/` | `/fs/usb0/timersResult` | `TimerSaveOptionsEnum.USB` -> `ResKeyPropertiesFactory.getUSBSavePath()` |
| SD | `/mnt/sd0` | `/mnt/sd0/timersResult` | `TimerSaveOptionsEnum.SDCard` / `SDCARD` -> `ResKeyPropertiesFactory.getSDSavePath()` |

**PROVED:** the Viper and Jeep `resKey.properties` members are byte-identical, SHA-256 `d467ab548e53a3a9c2b49abc2f2f84d520990ead8d6e802c3bf76d41e62781b2`, and contain `savePath_USB=/fs/usb0/`, `savePath_SD=/mnt/sd0`, and `save_folder_name=timersResult`. L-Series uses `common/resKey.properties`, SHA-256 `bcc9a2f313996b78564a86a0c66dd6b7e30e18b51d8b29c2311e95c902f9661b`, with snake-case `save_path_USB` and `save_path_SD` keys but the same values and folder.

**INFERRED:** these fixed roots name platform mount points. The application itself does not identify a device, enumerate volumes, validate a filesystem type, or invoke a mount service. The actual mount ownership and mount flags remain outside this Java evidence.

## Exact write dataflow

The old Viper/Jeep implementation is represented by class SHA-256 `65fbddc04b2e39e32c03028b1294c1a6b98e7062b82ef2e3a73d049428d06d7d`; L-Series is `d8cd498fc1cd7d9a2bcd622c3f11c0e754d4f2d9a19d73d15f3d0fe628be63c0`. The old enum class is `073c6998a7233c42b7a4fb2116341cadf1caae41161cf119161fbd78368ddcb2`; L-Series is `49b685bda44bd6d40e5ddaec48e3b3a0a3b5846838b27587f4b86eac8129b8ab`.

1. **PROVED:** `TimerSaveOptionsEnum.<clinit>()V` calls `getUSBSavePath()` at BCI 7 and `getSDSavePath()` at BCI 23 in the Viper/Jeep class, then stores those strings in the USB and SD option instances. L-Series has the same selection semantics.
2. **PROVED:** `TimerSavingData.saveDataTo(TimerSaveOptionsEnum,String,String)I` calls `enum.getDevicePath()` at BCI 1, then `isDeviceAvailable(String)` at BCI 9.
3. **PROVED:** `isDeviceAvailable(String)Z` constructs `new File(path)` at BCI 5 and calls `File.exists()` at BCI 10. Nothing in that method calls `isDirectory`, `canWrite`, a free-space API, or a platform media service.
4. **PROVED:** the old `saveDataTo` constructs `new File(devicePath,getSaveFolder())` at BCIs 47-59. L-Series uses BCIs 46-58. It checks `exists()` and uses the single-level `mkdir()`; failure returns status 24.
5. **PROVED:** old `createUpdateDownloadFile(File,String,String)File` redundantly calls `mkdirs()` if necessary at BCI 8, builds `dir.getAbsolutePath() + "/" + basename + getSuffix()` at BCIs 12-52, and calls `File.createNewFile()` at BCI 56. `getSuffix()String` returns `.html` at BCI 0. L-Series is semantically equivalent.
6. **PROVED:** only a `true` result from `createNewFile()` reaches `updateHTML` (old BCI 66). A pre-existing filename skips the write and still returns the `File`; `saveDataTo` then returns status 13. This is a success-reporting collision defect, not overwrite support.
7. **PROVED:** old `updateHTML(File,String)V` constructs `FileOutputStream(File)` at BCI 7, constructs `OutputStreamWriter(OutputStream,"UTF8")` at BCI 18, calls `Writer.write(String)` at BCI 26, flushes at BCI 31, and closes the file stream at BCI 39. There is no temporary file, rename, synchronization, fsync, or recovery record.

**PROVED:** the signed callers construct the basename from a finite localized timer-state label, `_`, `SimpleDateFormat("ddMMMMMyyyy_hhmma")` using the platform's current/default locale, `_`, and a fixed vehicle-line display name; `getSuffix()` then adds mandatory `.html`. Review of all 13 packaged L-Series timer-state locales and the fixed vehicle names found no slash or backslash, and no text-entry source reaches the basename. **UNKNOWN:** the writer performs no separator stripping, canonicalization, or containment check, and the platform locale's month/AM-PM tables are external to the packaged strings. The recovered callers do not prove ordinary directory-component control, but the evidence also cannot support a universal no-escape claim.

The Viper and Jeep `ResKeyPropertiesFactory` classes are byte-identical, SHA-256 `9771284c5033d0647ccc242dca164465d3d1293b7eb8a9c9b9b131dbbfb41a5a`; L-Series is `07ae321f5486c1909de8c63dacf41fc8c04643b5f112c2e7df96ac685a531d64`. **PROVED:** `loadProperties()V` loads the embedded resource through the class loader and `Properties.load(InputStream)`; its getters use `Properties.getProperty`. This closes the resource-to-enum-to-file path statically.

## Availability, failure, and removal semantics

| Property | Static conclusion | Evidence label |
|---|---|---|
| Root presence | `File.exists()` only | **PROVED** |
| Writable destination | No preflight check in the write chain | **PROVED** static negative within the selected methods |
| Directory identity | No `isDirectory()` check | **PROVED** static negative within the selected methods |
| Free space | No free-space query | **PROVED** static negative within the selected methods |
| Mount state/type/options | No mount-service or filesystem query | **PROVED** static negative within the selected methods |
| Removal/eject notification | No listener or media-status callback in this chain | **PROVED** static negative within the three packages' focused chain |
| Permission grant | Java policy/platform grants were not recovered from this call chain | **UNKNOWN** |
| Target write success | Requires the correct variant, timer data, mounted media, permission, space, and runtime I/O success | **TARGET OBSERVATION REQUIRED** |

**PROVED:** old `saveDataTo` maps `FileNotFoundException` to 23 and `IOException` to 24 across the save operation. `updateHTML` logs close failures and rethrows open/write `FileNotFoundException` or `IOException`. A removal or permission failure that manifests as one of those checked exceptions can therefore reach the status mapping. `SecurityException` is not caught by the shown handlers. Exact behavior for platform-specific removal, delayed writeback, or policy denial is **UNKNOWN**.

**INFERRED:** media removal after `createNewFile()` and before the final close can leave an empty or partial `.html` file because the sequence is non-atomic. The recovered code proves the vulnerable ordering, but a particular filesystem's persistence behavior requires target observation.

There is no filesystem fallback between USB and SD. **PROVED:** uConnect is a separate enum option with a null device path and a distinct upload path; it is not a retry destination for local write failure.

## Capability classification

This report assigns **level 2 of 5: statically proved, target-gated stock file write**. The package has a concrete stock UI-to-file construction and direct write primitive, and all three vehicle variants agree on the effective destinations. It remains target-gated because package selection, installation, authorization, media mount state, policy grant, and final persisted bytes have not been verified on the target.

The exported content is generated Performance Pages timer HTML. No method in the selected writer chain imports file bytes, executes content, or reopens the created file. The write is an ordinary output capability, not evidence of a USB-to-code or USB-to-application input route.

## Corpus boundary

The [focused consumer census](../reports/kim19_runtime_analysis/performance_pages_consumer_census.json) covered every class entry in all 19 KIM19 JARs and four nearby common-base JARs: 23 archives, 7,384 class entries, and zero classfile parse errors. Archive members were checked for the exact roots, folder, and HTML suffix; bytecode was checked for file I/O and candidate consumer edges. Negative statements in this report apply only to that selected corpus and those exact references. They do not establish absence from all firmware, a different KIM package, an unrecovered platform process, or a live target.
