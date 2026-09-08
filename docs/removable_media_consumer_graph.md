# Removable-media consumer graph

Research date: 2026-09-08. This graph asks whether any recovered KIM19 application or nearby common-base facility consumes the Performance Pages timer `.html` after it is written. Static presence, Java call reachability, and target operation are reported separately.

## Narrow conclusion

**PROVED:** Performance Pages has a complete static producer chain to `/fs/usb0/timersResult/<basename>.html` and `/mnt/sd0/timersResult/<basename>.html`.

**PROVED scoped negative:** across all 19 KIM19 JARs and four nearby common-base JARs, no non-Performance class contains the exact roots `/fs/usb0` or `/mnt/sd0`, the directory `timersResult`, or a direct invocation of the Performance writer. No non-Performance KIM class combines `.html`/`text/html` with a local file loader or viewer edge. The common base contains Apache HTML DOM and serializer classes, but no recovered KIM caller connects the exported path or filename to those classes.

**UNKNOWN:** the physical radio may expose the exported file to an unrecovered native component, another software package, or a computer after media removal. This scoped static census cannot prove global absence.

```text
Timer save UI
  -> TimerSaveOptionsEnum [PROVED static]
  -> fixed USB/SD root [PROVED static]
  -> timersResult/<basename>.html [PROVED static]
  -> FileOutputStream + UTF8 Writer [PROVED static]
  -> persisted removable-media file [TARGET OBSERVATION REQUIRED]
       |-> Performance Pages re-read [UNKNOWN; no reader edge]
       |-> another KIM19 application [UNKNOWN; no path/format/discovery edge found]
       |-> Kona HTML DOM/serializer [library present; no loader/render edge]
       |-> EcoDriveSvc [separate data-specific transfer service; no producer edge]
       `-> off-unit reader after media removal [outside recovered software corpus]
```

## Candidate chain status

| Producer -> storage -> candidate | Candidate role | Static reference | Write side | Read side | End-to-end status | Why it stops |
|---|---|---|---|---|---|---|
| Performance Pages -> USB/SD timer file -> Performance Pages | Writer **PROVED**; reader/viewer **UNKNOWN** | Producer **PROVED**; self-reader **UNKNOWN** | **PROVED** static, **TARGET OBSERVATION REQUIRED** runtime | **UNKNOWN** | **UNKNOWN** | Selected save code has no reopen/read path |
| Performance Pages -> USB/SD timer file -> DRMSync | Reader/writer | DRMSync file readers **PROVED**, timer reference absent in scope | **PROVED** static | **UNKNOWN** | **UNKNOWN** | DRMSync concrete paths are internal `/fs/mmc1/download`, with no timer filename, HTML, removable root, or directory enumeration link |
| Performance Pages -> USB/SD timer file -> Store Base64 | Reader/writer codec utility; importer/exporter entry role **UNKNOWN** | File helper **PROVED** present | **PROVED** static | **UNKNOWN** | **UNKNOWN** | No caller to Base64 file entry points outside that utility, no removable path, discovery, or HTML match |
| Performance Pages -> USB/SD timer file -> Kona HTML DOM/serializer | Parser/serializer; viewer **UNKNOWN** | Library classes **PROVED** present | **PROVED** static | **UNKNOWN** | **UNKNOWN** | Parser/serializer primitives are not a file chooser, browser, or render path; no KIM caller bridges the file |
| Performance Pages -> USB/SD timer file -> Kona FileIO | Reader/writer/enumerator service | Service API **PROVED** present | **PROVED** static | **UNKNOWN** | **UNKNOWN** | FileIO manages permission-gated application/MMC1 operations; no Performance caller or USB/SD path link |
| Performance Pages -> USB/SD timer file -> EcoDrive | Uploader/exporter/enumerator service | USB transfer API **PROVED** present | **PROVED** static | **UNKNOWN** | **UNKNOWN** | `startUSBTransfer` belongs to a separate EcoDrive data namespace and has no Performance/KIM caller |
| Performance Pages -> USB/SD timer file -> external computer | Reader/viewer outside corpus | Export format/path **PROVED** static | **PROVED** static, runtime **TARGET OBSERVATION REQUIRED** | **UNKNOWN** | **TARGET OBSERVATION REQUIRED** | Persisted file and external readability require an authorized target observation |

For the **UNKNOWN** read/end-to-end rows, the candidate edge was sought in this bounded corpus and no matching syntactic construction was found. **UNKNOWN** does not mean the software can never consume such a file under every firmware or runtime condition.

## Candidate detail

### DRMSync

**PROVED:** `MTSSRTBrandDetailRequest` (class SHA-256 `ddeb62723af0cbca1587c59badf25ba829ccdd0cea2466a1f3ed36985048bf74`) reads `/fs/mmc1/download/isSRT` in `processJSONObject(Lorg/json/me/JSONObject;)V` through `FileInputStream(File)` at BCI 35. `writeToBrandFile(Z)V` constructs the fixed file at BCI 25, deletes at BCI 52, creates at BCI 57, opens `FileOutputStream(File,Z)` at BCI 78, and writes at BCIs 108 or 135. `MTSContentStreamRequest.processStream(Ljava/io/InputStream;)V` calls `HuDRMFileManager.saveBytesToFile(Ljava/io/InputStream;Ljava/io/File;)J` at BCI 198; `MTSGrantPayloadRequest.processStream(Ljava/io/InputStream;)V` calls it at BCI 77. The manager class SHA-256 is `0bd70dfaf96b333f33653b61a433642303a970d09f4ebe1d19a9d280f776f065`. These are real file consumers/producers in the KIM19 application set, but their concrete storage is internal and their data arrives through DRM workflows. No edge uses either timer root, `timersResult`, or `.html`.

### Store Base64

**PROVED:** `com.sprint.chrysler.storefront.communications.Base64` (class SHA-256 `e22903749ded2682b2788aeaee18ee4d055387d1bbafb6d8f6e0da13a5e0eea7`) exposes file encode/decode helpers. `decodeFromFile(Ljava/lang/String;)[B` opens `FileInputStream(File)` at BCI 90; `encodeFromFile(Ljava/lang/String;)Ljava/lang/String;` opens it at BCI 53; `encodeToFile([BLjava/lang/String;)V` and `decodeToFile(Ljava/lang/String;Ljava/lang/String;)V` open `FileOutputStream(String)` at BCIs 25 and 11. The only selected calls to these entry points are self-calls: `encodeFileToFile(Ljava/lang/String;Ljava/lang/String;)V` -> `encodeFromFile` at BCI 1 and `decodeFileToFile(Ljava/lang/String;Ljava/lang/String;)V` -> `decodeFromFile` at BCI 1. No other class calls a Base64 file entry point in the scoped archives. Static utility presence therefore does not establish runtime reachability or timer-file handling.

### Common-base HTML classes

**PROVED:** `base/kona/lib/kona.jar` contains `org/apache/html/dom`, W3C HTML interfaces, and XML serializer/parser support. The focused invocation census finds no call from outside those implementation packages that constructs a timer-file reader or renderer. HTML-related type names are insufficient to promote this to a consumer.

### Kona FileIO

**PROVED:** `kona.fileio.FileIOManager.getInstance()` constructs `com.harman.fileio.FileIOManagerImpl`. `FileImpl` checks `FileIOPermission("read")` or `FileIOPermission("write")`; `FileIOManagerImpl` requests write access and calls `PlatformService.changeMMC1Mode("w")`, then later returns it to read mode. No Performance or other KIM19 class invokes this service in connection with the exported file. It is a separate application-storage boundary.

### EcoDrive

**PROVED:** the common Java API exposes USB status and transfer operations through `EcoDriveImpl`, which invokes the `com.harman.service.EcoDrive` service. The corresponding recovered native `EcoDriveSvc` has a data-specific flash source `/fs/etfs/usr/var/ecoDrive/data`; its transfer selects the discovered USB device plus `/Uconnect/ecodrive/data` or `/iFiat/ecodrive/data` and uses a `/tmp.tmp` intermediate during the copy/rename flow. This is evidence of an adjacent USB export service, not an HTML consumer. No Performance/KIM Java edge invokes it. Exact native addresses and function hashes are in [the bounded EcoDrive report](ecodrive_native_storage_boundary.md) and its [machine-readable evidence](../reports/kim19_runtime_analysis/performance_pages_native_storage.json).

## Residual target boundary

**TARGET OBSERVATION REQUIRED:** persisted output remains conditional on the correct already-installed and authorized variant, writable mounted media, the effective Java grant, successful close/writeback, and durable bytes. **UNKNOWN:** no supported on-unit selector or reader for the exported file is established. These unresolved facts remain target boundaries; this report does not add a target action.

## Reproduce the scoped census

The canonical [consumer census report](../reports/kim19_runtime_analysis/performance_pages_consumer_census.json) is regenerated from the read-only recovered corpus with:

```powershell
python -m analysis_tools.performance_pages_consumer_census --corpus $corpusWork
python -m analysis_tools.performance_pages_consumer_census --corpus $corpusWork --check
python -m unittest analysis_tools.tests.test_performance_pages_consumer_census
```

The report preserves all 23 archive hashes, exact class counts, allowlisted path/format literal-substring evidence, and selected invocation metadata. Its zero-count fields are syntactic findings; its runtime conclusion remains **UNKNOWN**.
