# Performance Pages variant inventory

Research date: 2026-09-08. This is a static inventory of the three Performance Pages packages in the recovered RA4 18.45.01 KIM19 corpus. All hashes refer to the unmodified recovered artifacts. The canonical machine-readable producer evidence is [performance_pages_export_notes.json](../analysis_tools/performance_pages_export_notes.json); selected class methods are independently hash- and BCI-bound in the generated class-evidence report.

## Inventory result

**PROVED:** KIM19 contains three separately configured Performance Pages Xlets. Each has its own application UUID, JAR, version, vehicle-line predicate, and embedded resources. All use `com.sprint.gskills.xlet.GSkillsXlet`, application category 2, `full.policy`/`security.policy`, `PauseAllowed=true`, and a `VC_PP_Prsnt:1` visibility predicate.

| Variant | UUID | Version | Display identity | Vehicle predicate | JAR SHA-256 |
|---|---|---:|---|---|---|
| Viper | `52c79381-6719-11e1-b86c-0800200c9a66` | 01.23.01 | SRT Performance Pages | `VC_VEH_LINE:43` | `00b15a1d7268565c3644ba07e1fb1c3789f27b9b118029510652d03139d3ad0d` |
| Jeep | `6BFD02C0-40C3-11E2-A25F-0800200C9A66` | 01.57.01 | SRT Performance Pages | `VC_VEH_LINE:1` | `bfcfe3fdc6bf978c36e6e50860458e1def531b09ca046725312a373cf935f566` |
| L-Series | `7DEC7834-535D-47B5-BD33-695477EDCD57` | 02.01.01 | Performance Pages | `VC_VEH_LINE:{44;41;2}` | `8a421cfda32d05f29d92e263d62307623a1603ec4e2d3c9183ca69b2ff33d4f6` |

The external `xlet.properties` hashes are respectively `31b87d65595efefc4bb15837b6cbeeb599212f115350b84a3c2d82fa40d4ebd1`, `7e906bf83fad01f2dec412b8ec79b51d34e96af979bae5e7289afc6d9c21c9b8`, and `e970a65dd160828a505d1695d926d27932bb598b75a656f6fb3014de8cc1d619`. The JARs have no `META-INF/MANIFEST.MF`; their embedded `xlet.properties` repeats the main class, UUID, version, policy, category, display identity, and show conditions.

## Configuration and dependencies

**PROVED:** Viper and Jeep have byte-identical embedded `resKey.properties`, SHA-256 `d467ab548e53a3a9c2b49abc2f2f84d520990ead8d6e802c3bf76d41e62781b2`. L-Series uses a reorganized `common/resKey.properties`, SHA-256 `bcc9a2f313996b78564a86a0c66dd6b7e30e18b51d8b29c2311e95c902f9661b`. Key names changed from camel case to snake case, but local export values did not:

| Purpose | Viper/Jeep key and value | L-Series key and value |
|---|---|---|
| USB root | `savePath_USB=/fs/usb0/` | `save_path_USB=/fs/usb0/` |
| SD root | `savePath_SD=/mnt/sd0` | `save_path_SD=/mnt/sd0` |
| Child folder | `save_folder_name=timersResult` | `save_folder_name=timersResult` |
| Upload service type | `serviceType=130` | `service_type=130` |
| Shared resources | `use_shared_resources=false` | `use_shared_resources=false` |

`TimerSaveOptionsEnum.<clinit>()V` calls `ResKeyPropertiesFactory.getUSBSavePath()` at BCI 7 and `getSDSavePath()` at BCI 23 in all three recovered enum classes. Local export then uses direct `java.io.File` and writer APIs. It does not delegate USB/SD output to the upload implementation or to a generic platform storage service. The distinct uConnect option has a null local device path and enters the upload branch.

## Exact implementation comparison

The Viper archive contains 848 members and Jeep 849. They share 848 member names; 844 shared members are byte-identical. The four changed resources are `GSkillsTheme.res`, `LegalDisclaimer.res`, `valueRange.properties`, and embedded `xlet.properties`; Jeep alone adds `LegalDisclaimer_CH.res`. **PROVED:** every class file, including the complete export UI, filename generator, HTML generator, and writer, is byte-identical between Viper and Jeep. This conclusion comes from member-byte comparison, rather than class-name similarity.

Relevant identical Viper/Jeep class hashes are:

| Class | SHA-256 |
|---|---|
| `com/sprint/gskills/view/CommonTimerViewContainer` | `5f84b61804730940e54f74c6b0be624af1a9dae24ad9b4c9e537b0a8bb2033af` |
| `com/sprint/gskills/controller/savetimerrun/TimerSavingData` | `65fbddc04b2e39e32c03028b1294c1a6b98e7062b82ef2e3a73d049428d06d7d` |
| `com/sprint/gskills/constants/TimerSaveOptionsEnum` | `073c6998a7233c42b7a4fb2116341cadf1caae41161cf119161fbd78368ddcb2` |
| `com/sprint/gskills/view/mainview/MainView` | `42042a8cfc82fe69ac49674ef70b8730a55b9f1dd2dde7f0e3bb074055463144` |

The L-Series archive contains 879 members. Against Viper it has 723 common member names, 675 byte-identical common members, 48 changed common members, and a substantial package/UI reorganization. The old `view/CommonTimerViewContainer` and `view/timerview/*` path becomes `view/timers/CommonTimerView` and `view/timers/components/*`. Relevant L-Series hashes are `a07323202b8ed43ccc49b72108f70c387a86adc5b6e847631e5c5401d74c2a1b` for `CommonTimerView`, `d8cd498fc1cd7d9a2bcd622c3f11c0e754d4f2d9a19d73d15f3d0fe628be63c0` for `TimerSavingData`, and `49b685bda44bd6d40e5ddaec48e3b3a0a3b5846838b27587f4b86eac8129b8ab` for `TimerSaveOptionsEnum`.

**PROVED:** L-Series is not bytecode-identical to the old variants, but it implements the same constrained local file primitive:

- Save and fixed USB/SD choice reach a common timer view.
- One `Date` is passed to fixed-template HTML and application basename generators.
- `TimerSavingData.saveDataTo` joins a fixed media root and `timersResult`.
- `createUpdateDownloadFile` appends mandatory `.html`, uses `createNewFile`, and calls `updateHTML` only for a new file.
- `updateHTML` writes the generated string through `OutputStreamWriter(...,"UTF8")`.

The differences are meaningful at the timer/report layer. Viper/Jeep export 0-60, eighth-mile elapsed time and speed, quarter-mile elapsed time and speed, plus optional braking distance and speed. L-Series adds reaction time and 0-100, conditionally adds 60-foot, retains the eighth- and quarter-mile pairs, and retains optional braking distance and speed. L-Series gets vehicle display names from fixed `VehicleLineEnum` values (`300`, `Charger`, `Challenger`, and unsupported state); Viper/Jeep use packaged `vehicle_line_1=Jeep` and `vehicle_line_43=Viper` mappings.

## Timer, upload, and removable-media roles

**PROVED:** all variants contain timer display/model code, a local removable-media branch, and a separate upload branch. `updateDialogAndButtons(TimerSaveOptionsEnum)V` distinguishes SAVE, uConnect, USB, and SD options. USB/SD call `TimerSavingData.saveDataTo`; uConnect calls the upload controller. Shared UI and resource libraries do not merge those destinations.

**INFERRED:** the narrowest common role is a fixed-format timer-report producer with a separate fixed timer-upload client. Equivalent local output behavior across the three variants is established by the exact calls and constants above. No claim of semantic equivalence is based only on naming.

**TARGET OBSERVATION REQUIRED:** static presence and `xlet.showConditions` do not establish which variant a target selects, whether it is launch-authorized, whether its timer model is populated, or whether media is mounted and writable.

## Evidence boundary

The source artifacts and selected BCI tuples are canonicalized in [performance_pages_export_notes.json](../analysis_tools/performance_pages_export_notes.json). The call graph is detailed in [performance_pages_export_call_graph.md](performance_pages_export_call_graph.md), filename control in the generated [filename dataflow](../reports/kim19_runtime_analysis/performance_pages_filename_dataflow.json), and content fields in [performance_pages_html_generation.md](performance_pages_html_generation.md). No recovered vendor binary was modified or committed.
