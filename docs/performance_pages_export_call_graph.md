# Performance Pages export call graph

Research date: 2026-09-08. This report traces the ordinary local timer export from stock UI action to result UI for all three recovered KIM19 Performance Pages variants. Viper and Jeep use byte-identical classes; L-Series is traced separately. The recovered code was checked both with the repository classfile parser and JDK 8 `javap -c -p -s` output. Static reachability after the listed gates is **PROVED**; execution on a radio remains **TARGET OBSERVATION REQUIRED**.

## Gates and inputs

The outer Xlet predicates are `VC_PP_Prsnt:1` plus vehicle line 43 for Viper, line 1 for Jeep, or one of 44, 41, and 2 for L-Series. Inside the timer UI, the user chooses Save and then one fixed option: USB, SD, or the separate uConnect upload path. USB and SD are local-file choices. They carry a `TimerSaveOptionsEnum`, not a path, filename, or body string.

```text
timer summary Save
  -> SAVE view transition
  -> fixed USB or SD button
  -> fixed TimerSaveOptionsEnum
  -> one Date
  -> fixed-template HTML + application basename
  -> TimerSavingData.saveDataTo(enum, html, basename)
  -> media-root existence -> timersResult mkdir
  -> createNewFile -> UTF8 writer
  -> integer status -> localized status UI
```

## Viper and Jeep UI-to-export path

All classes in these two JARs are byte-identical. The steps below therefore bind independently to both source JAR hashes while sharing the same BCIs.

1. `com.sprint.gskills.view.timerview.TimerTypeButtonsContainer$4.actionPerformed(ActionEvent)V` handles the timer-summary Save button. It calls the controller accessor at BCI 11, reads `TimerSaveOptionsEnum.SAVE` at BCI 14, and calls `GSkillsViewController.notifyDisplayViewChanged(TimerSaveOptionsEnum)` at BCI 17.
2. `GSkillsViewController.notifyDisplayViewChanged(TimerSaveOptionsEnum)V` obtains its `MainView` and calls `MainView.updateRightScreen(TimerSaveOptionsEnum)` at BCI 5.
3. `MainView.updateRightScreen(TimerSaveOptionsEnum)V` calls `GSkillsViewBuildFactory.getTimerContainer(TimerSaveOptionsEnum)` at BCI 5 and replaces the right screen with the returned container.
4. `GSkillsViewBuildFactory.getTimerContainer(TimerSaveOptionsEnum)Container` obtains the timer view by code at BCI 4 and invokes `CommonTimerViewContainer.updateDialogAndButtons(TimerSaveOptionsEnum)` at BCI 13. For `SAVE`, that view installs the fixed save-choice dialog and buttons.
5. `TimerSaveButtonContainer$1.actionPerformed(ActionEvent)V` handles USB: it reads `TimerSaveOptionsEnum.USB` at BCI 14 and calls `MainView.updateRightScreen` at BCI 17. `$2.actionPerformed` has the same BCIs for `SDCard`. The MainView/factory/common-view path repeats with the local destination enum.
6. `CommonTimerViewContainer.updateDialogAndButtons(TimerSaveOptionsEnum)V` constructs one `Date` at BCI 4. In the USB/SD branch it obtains `TimerSavingData` at BCI 189, calls `convertDataToHtml(Date)` at BCI 195, calls `getFileName(Date)` with the same `Date` at BCI 200, and calls `saveDataTo(enum,html,basename)` at BCI 203. It passes the returned integer to `updateViewWithSaveStatus` at BCI 210, then replaces the central dialog and button container.

The method also has a separate uConnect branch at BCIs 162-186: it generates HTML/name and calls `UploadTimerRunController.submitUploadTask`. That branch is not a fallback for USB/SD failure and does not participate in local file creation.

## L-Series UI-to-export path

L-Series reorganizes the packages and timer fields, but preserves the local invocation shape.

1. `com.sprint.gskills.view.timers.components.TimerTypeButtonsContainer$1.actionPerformed(ActionEvent)V` calls the controller accessor at BCI 10, reads `TimerSaveOptionsEnum.SAVE` at BCI 13, and invokes `GSkillsViewController.notifyDisplayViewChanged` at BCI 16.
2. The controller calls `MainView.updateRightScreen(TimerSaveOptionsEnum)` at BCI 5. MainView calls `GSkillsViewBuildFactory.getTimerContainer` at BCI 6, and the factory calls `CommonTimerView.updateDialogAndButtons` at BCI 13.
3. `TimerSaveButtonContainer$1.actionPerformed` selects `USB` at BCI 9 and calls `MainView.updateRightScreen` at BCI 12. `$2` selects `SDCARD` at BCI 9 and calls MainView at BCI 12.
4. `CommonTimerView.updateDialogAndButtons(TimerSaveOptionsEnum)V` constructs one `Date` at BCI 4. The local branch gets the singleton `TimerSavingData` at BCI 193, calls `convertDataToHtml(Date)` at BCI 199, calls its filename method `toString(Date)` at BCI 204, calls `saveDataTo` at BCI 207, and calls `updateViewWithSaveStatus` at BCI 214.

The method name `toString(Date)` is overloaded as an application filename formatter; no semantic equivalence was inferred from its name. Its instructions and call sites were inspected directly.

## Timer data and HTML arguments

**PROVED:** the writer receives one complete application-generated HTML `String`. It is not passed a user-selected input file or arbitrary byte buffer.

In Viper/Jeep, concrete Best, Current, and Last metric/US view listeners transfer timer-model values into the common timer view fields and labels. `convertDataToHtml(Date)String` reads label text for 0-60, eighth-mile elapsed/speed, quarter-mile elapsed/speed, and optional braking distance/speed.

In L-Series, `CommonTimerView.updateTimerValueLabels()V` calls `setReactionTime` at BCI 1, `setZeroToSixtyValue` at 5, `setZeroToHunderedValue` at 9, `setEigthValue` at 13, `setQuarterValue` at 17, conditional `setSixtyFeetValue` at 28, and `setBrakeDistance` at 42. These setters obtain timer-model numeric values, format them, and place them in `FastNumberLabel`/`CommonLabel` instances. The HTML generator reads those labels. The timer/vehicle model influences numeric output and fixed-row presence; no user-entered string field is recovered.

The complete HTML structure and field classifications are in [performance_pages_html_generation.md](performance_pages_html_generation.md).

## Filename and final path

Viper/Jeep `CommonTimerViewContainer.getFileName(Date)String` and L-Series `CommonTimerView.toString(Date)String` each have 61 bytecode instructions and the same filename operations:

1. Append the resource value for `timer_state_` plus the fixed timer-state title. The old method calls `TimersDisplayStatusEnum.getTitleName()` at BCI 30; L-Series calls the enum's `toString()` at BCI 30. Resource lookup is at BCI 39.
2. Call `replaceTimerType(value,"|","i")` at BCI 46. This recursive application helper replaces all vertical bars in this one component.
3. Append `_` at BCI 54.
4. Construct `SimpleDateFormat("ddMMMMMyyyy_hhmma", platformLocale)` at BCI 72 after `PlatformInfo.getCurrentLocale()` at BCI 69. If `PlatformException` is caught at handler BCI 79, construct the same pattern with the default locale at BCI 87. Format the same export `Date` at BCI 94.
5. Append `_` at BCI 102, then append vehicle line. Viper/Jeep call `GSkillsStateManager.getVehicleLine()` at BCI 112 and `ResKeyPropertiesFactory.getVehicleLineName(int)` at BCI 115. L-Series calls `GSkillsStateManager.getVehicleLine()` at 112 and `VehicleLineEnum.getDisplayName()` at 115.

`TimerSaveOptionsEnum.<clinit>()V` binds USB to the packaged USB root at BCI 7 and SD to the packaged SD root at BCI 23. `TimerSavingData.saveDataTo(TimerSaveOptionsEnum,String,String)I` performs the path sequence:

| Operation | Viper/Jeep BCI | L-Series BCI | Result |
|---|---:|---:|---|
| `enum.getDevicePath()` | 1 | 1 | Fixed selected root |
| `isDeviceAvailable(path)` | 9 | 9 | `new File(path).exists()` only |
| `new File(root,getSaveFolder())` | 56 constructor | 55 constructor | Fixed `timersResult` child |
| `directory.exists()` | 63 | 62 | Skip or attempt creation |
| `directory.mkdir()` | 71 | 70 | False maps to status 24 |
| `createUpdateDownloadFile(dir,html,basename)` | 85 | 84 | Final file construction/write |

`createUpdateDownloadFile(File,String,String)File` redundantly calls `mkdirs()` at BCI 8 if necessary, then constructs `dir.getAbsolutePath() + "/" + basename + getSuffix()` through BCIs 20-49. `getSuffix()String` returns literal `.html` at BCI 0. It calls `File.createNewFile()` at BCI 56 and calls `updateHTML` at BCI 66 only when that result is true.

The generated [filename dataflow](../reports/kim19_runtime_analysis/performance_pages_filename_dataflow.json) contains the five requested control answers and provenance. The code has no canonicalization or containment check.

The five control questions resolve as follows:

1. **Is the filename completely application-controlled?** No in the literal source sense. The application fixes the construction and accepts no filename string, but platform date/locale output and vehicle-line state supply characters. The finite timer-state choice selects one packaged localized label.
2. **Can ordinary user input influence any part?** Yes, in a bounded way: the user selects a fixed timer state/report and can change platform locale/time through supported settings. No text-entry value, arbitrary identifier, or selected source filename reaches the basename. This finite/indirect influence does not establish Level 3 free filename control.
3. **Can ordinary user input influence directory components?** The user selects the fixed USB or SD enum. The corresponding packaged root and `timersResult` child are fixed; no ordinary UI supplies or edits a directory string.
4. **Is `.html` mandatory?** Yes. `getSuffix()String` returns literal `.html`, and the only local writer appends it after the generated basename.
5. **Can the destination escape `timersResult`?** No ordinary escaping input is proved. All 13 packaged L-Series timer-state locale values and all fixed vehicle display names were reviewed and contain no slash or backslash. The fixed date pattern also contains no separator. The implementation nevertheless has no separator stripping, canonicalization, or post-join containment check, and the platform locale month/AM-PM tables are not inside the recovered JARs. A universal never-escapes claim is therefore **UNKNOWN**, rather than proved. No traversal value was constructed or tested.

## Write, flush, close, and return statuses

Both generations use the same write sequence in `TimerSavingData.updateHTML(File,String)V`:

| Operation | BCI | Data/state |
|---|---:|---|
| `new FileOutputStream(file)` | 7 | Opens the newly created final path directly |
| load `UTF8` | 16 | Encoding name |
| `new OutputStreamWriter(stream,"UTF8")` | 18 | Character-to-byte conversion |
| `Writer.write(html)` | 26 | Writes the complete String |
| `Writer.flush()` | 31 | Flushes the writer |
| `FileOutputStream.close()` | 39 | Closes the underlying stream; the writer itself is not closed |

There is no temporary file, atomic rename, overwrite mode, explicit synchronization, or rollback. A `createNewFile()` false result skips the writer but still reaches the outer success return.

Old `saveDataTo` returns status 23 for a missing device path at BCIs 44-46, 24 for `mkdir()` false at 77-79, and 13 after `createUpdateDownloadFile` at 89-91. Its `FileNotFoundException` handler starts at BCI 92 and returns 23; its `IOException` handler starts at 97 and returns 24. L-Series uses returns 43-45, 76-78, and 88-90, with handlers at 91 and 96.

Exception handling in `updateHTML` is deliberately asymmetric:

- Viper/Jeep rethrow `FileNotFoundException` at BCI 99 and other `IOException` at BCI 135. L-Series rethrows at BCIs 97 and 132. File open, writer construction, write, and flush failures therefore reach the outer 23/24 mapping.
- Viper/Jeep close handlers at BCIs 45 and 149 log and suppress close-only `IOException`; L-Series uses BCIs 45 and 146. A close failure does not replace the otherwise normal result.
- A checked failure after `createNewFile()` can leave an empty or partial final file. No delete is recovered.
- `SecurityException` and runtime failures in HTML/filename generation are not mapped by the shown local handlers. Their exact resulting UI is **UNKNOWN**.

## Result UI and retry semantics

`updateViewWithSaveStatus(int,enum)` stores the status/selection, creates status text areas, calls `setTextWithSaveStatus()V`, and displays a fixed OK button. Both generations use the same resource IDs:

| Status | Packaged resource IDs | Recovered trigger | Displayed meaning |
|---:|---|---|---|
| 13 | `timer_mes_succeed` | Normal write, suppressed close error, or existing-name no-write branch | `SAVE SUCCESSFUL` in recovered English resources |
| 23 | `timer_mes_error_cannotSave` + `timer_mes_info_NotFound` | Missing device root or `FileNotFoundException` | `Cannot Save Run`; Viper/Jeep package `[type] unava|lable.`, while L-Series packages `[type] unavailable.` |
| 24 | `timer_mes_error_cannotSave` + `timer_mes_info_full` | Directory-create false or `IOException` from open/write/flush | `Cannot Save Run` / `[type] full` |

For statuses 23 and 24, `[type]` is replaced with the localized name for the selected fixed media enum. There is no automatic retry. OK returns to the timer summary, from which the user can invoke Save again. A same-minute retry can collide with the empty/partial file and receive false success.

The canonical [failure-signature report](../reports/kim19_runtime_analysis/performance_pages_export_failure_signatures.json) keeps packaged strings separate from inferred meaning and distinguishes rethrown I/O failures from suppressed close errors.

## Static boundary

**PROVED:** a conditional ordinary UI path reaches direct final-path file creation and UTF-8 timer HTML output in every recovered variant. **INFERRED:** its narrowest capability is a Level 2 fixed-destination, application-generated report export. **UNKNOWN:** static code does not establish launch authorization, live timer data, platform locale alphabet, permission, writable media, persistence after removal, or durable bytes after a close error. No static file-write fact is promoted to target success or to a consumer handoff.
