# Performance Pages file-write capability

**INFERRED capability classification: Level 2**, supported by the **PROVED**
static path - a fixed application-selected destination and variable
application-generated filename/content. This classification applies
to the recovered ordinary timer-export call path. Its execution on the user's
radio remains **TARGET OBSERVATION REQUIRED**.

**INFERRED stopping assessment: Outcome A.** Performance Pages supplies a
constrained timer-report export. The focused KIM19/common-base investigation
does not establish another signed application discovering and consuming that
export. The result supports ordinary data export, with no proved reusable
cross-application file-transfer primitive.

## Exact capability boundary

| Dimension | Recovered behavior | Evidence |
|---|---|---|
| UI activation | Timer save action followed by USB or SD selection | [UI-to-file call graph](performance_pages_export_call_graph.md) |
| Destination | Packaged USB `/fs/usb0/` or SD `/mnt/sd0`, plus `timersResult` | `TimerSaveOptionsEnum.<clinit>`, `ResKeyPropertiesFactory` getters, `TimerSavingData.saveDataTo` |
| Filename | Localized timer-state label, formatted date/time, packaged vehicle-line name, mandatory `.html` | View filename generator and `TimerSavingData.getSuffix` |
| Content | Generated timer HTML, localized labels/units, timer display values, platform date/time | View HTML generator; [field dataflow](../reports/kim19_runtime_analysis/performance_pages_html_fields.json) |
| File creation | `File.createNewFile`; writer called only when it returns true | `createUpdateDownloadFile`, BCI56/59/66 in the shared older implementation |
| Byte write | `FileOutputStream(File)`, `OutputStreamWriter(...,"UTF8")`, `Writer.write`, `Writer.flush`, stream close | `TimerSavingData.updateHTML`, BCI7/18/26/31/39 |
| Consumer | No complete ordinary timer-export reader chain established | [Consumer graph](removable_media_consumer_graph.md) |

The [variant inventory](performance_pages_variant_inventory.md) binds the exact
JAR and class identities. Shared class names do not establish equivalence;
the older Jeep/Viper writer class bytes match, while L-Series has a different
implementation with the same constrained primitive. The generated
[filename report](../reports/kim19_runtime_analysis/performance_pages_filename_dataflow.json)
records the corresponding variant-specific evidence.

## Why this is Level 2

**PROVED:** Level 0 understates the concrete conditional UI-to-file code path.
Level 1 understates the variable date/time, timer-state and measurement content.
The application constructs every filename component from its packaged values,
timer state and platform values; the user chooses among stock actions and can
indirectly influence measurements or settings. No free-text filename, directory,
document body, or source-file picker enters the recovered export path.

**INFERRED classification rule:** finite stock report/state selection and
indirect influence on telemetry/time/locale are recorded explicitly as indirect
influence. They do not establish Level 3's stronger controllable filename or
substantial freely supplied content. The narrowest category fully supported is
therefore Level 2, with those documented input qualifications.

**UNKNOWN:** the absence of an ordinary free-text source does not prove a
filesystem containment defense. The writer has no general path canonicalization
or separator-stripping check. Host filesystem links, unexpected platform strings,
changed configuration or concurrent filesystem mutation were not exercised.
No arbitrary path or arbitrary-content behavior is inferred from a Java method
accepting `String` arguments: the actual signed callers determine the usable
capability. Levels 4 and 5 are not established.

## Reliability limits

**PROVED:** a name collision is a no-write success: `createNewFile()` returning
false skips `updateHTML`, then the outer method returns the normal success
status. There is no incremented name, overwrite retry or temporary-file strategy
on this timer path. The filename timestamp has minute precision, so separate
saves can select the same application-generated name.

**PROVED:** open/write/flush exceptions are rethrown toward the save-status
mapping. Close exceptions are logged and suppressed. A failed write can leave
an empty or partial newly created file, and a later same-name retry can encounter
that file and take the no-write-success branch. A displayed success message is
therefore insufficient evidence of complete bytes on media. Exact packaged UI
strings are separated from interpretation in the
[failure-signature report](../reports/kim19_runtime_analysis/performance_pages_export_failure_signatures.json).

**PROVED:** the application checks device-path existence, not a platform mount
record. It has no explicit free-space or writable-media check. Actual mounted
media, permissions, launch authorization, timer-state availability and durable
write success remain **TARGET OBSERVATION REQUIRED**.

## Shared services and handoff

**PROVED scoped result:** the focused consumer analysis covers the KIM19 JARs
and recovered common Java base. Common FileIO and EcoDrive APIs exist, but no
KIM19 caller or file-discovery edge joins them to `timersResult`.
The [bounded native EcoDrive trace](ecodrive_native_storage_boundary.md) finds
a separate fixed internal data source and EcoDrive-specific USB destinations.
Those interfaces do not promote Performance Pages to a generic storage service.

**UNKNOWN:** no scoped static survey proves that every component on a live
radio lacks a consumer. The current finding is that a useful ordinary signed
producer-to-storage-to-consumer chain is not established by the recovered
evidence examined here.
