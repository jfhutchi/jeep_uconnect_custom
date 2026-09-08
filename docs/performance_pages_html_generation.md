# Performance Pages HTML generation

Research date: 2026-09-08. This report reconstructs `convertDataToHtml(Date)String` in the three recovered KIM19 Performance Pages variants and follows the returned string through `TimerSavingData.updateHTML(File,String)V`. The canonical field inventory is the generated [performance_pages_html_fields.json](../reports/kim19_runtime_analysis/performance_pages_html_fields.json).

## Result

**PROVED:** all three variants generate a fixed HTML table whose dynamic text consists of platform date/time and localization values plus vehicle/timer measurements. Viper and Jeep use the same class bytes. L-Series uses a redesigned view/model and adds fields, but retains the same fixed document skeleton and UTF-8 writer.

The content classification is `fixed_template_runtime_values`. No filename, body, tag, attribute, CSS, JavaScript, link, form, external resource, selected input file, or free-text field is accepted from the ordinary save UI. HTML generation alone does not establish script execution, rendering, import, or a stock consumer.

## Fixed template

The generator concatenates one Java `String`; it does not use a template file or DOM. Whitespace below is added for readability. The actual fixed structure is emitted without line breaks:

```html
<html><head> <title>[localized title]</title><meta http-equiv="Content-Type" content="text/html;charset=utf-8"></meta></head><body><h2>[date]--UTC[timezone suffix]</h2><table  border="1" frame = "border"><tr><td>[localized timer column]</td><td></td></tr>[fixed timer rows]</table></body></html>
```

Each timer row has this literal form:

```html
<tr><td>[localized row label]</td><td>[formatted value] [localized unit]</td></tr>
```

Viper/Jeep literal BCIs include `<html>` at 58, `<head> <title>` at 73, resource ID `timer_save_file_title` at 82, the UTF-8 meta literal at 104, `<table  border="1" frame = "border">` at 160, the first measurement row at 224, and closing `</table>`, `</body>`, `</html>` at 700, 709, and 718. L-Series uses the same structural literals through BCI 202; measurement rows begin at 223 and close at 890, 898, and 906.

Both methods call `replaceTimerType(completeHtml,"|","i")` as their final transformation: old BCIs 731-735 and L-Series 918-922. This is a packaged-resource character convention, not HTML escaping.

## Complete field classification

The control terms below use the requested taxonomy exactly. No dynamic field is classified as user-controlled. Ordinary driving and settings can influence telemetry, locale, units, and time; their direct producing authority remains separated below.

| Output field | Variants | Source and formatting | Control |
|---|---|---|---|
| HTML tags, attributes, row order | All | String literals in `convertDataToHtml` | fixed |
| Document title | All | localized `timer_save_file_title` | platform-controlled |
| Date/time in `h2` | All | same export `Date`, `SimpleDateFormat("MM/d/yy h:mm a")` default locale | platform-controlled |
| Timezone suffix | All | `"UTC" + format.getTimeZone().getDisplayName().substring(3)` | platform-controlled |
| Column heading | All | localized `timer_save_column_timer` | platform-controlled |
| Row labels | Old | localized 0-60, eighth elapsed/speed, quarter elapsed/speed, braking distance/speed labels | platform-controlled |
| Row labels | L-Series | localized reaction, 0-60, 0-100, eighth elapsed/speed, quarter elapsed/speed, 60-foot, braking distance/speed labels | platform-controlled |
| Units | All | packaged localized seconds, distance, and speed unit labels selected with platform locale/unit state | platform-controlled |
| Reaction time | L-Series | `CommonTimerModel.getReactionTimeValue`; subtract 1.26 if raw value is below 2.53, format `#0.00`, otherwise `--` | vehicle-controlled |
| 0-60 time | All | old listener supplies `setZeroToSixtyValue(String)`; L-Series `getZeroToSixtyValue`, accept greater than 0 and less than 25.3 else `--` | vehicle-controlled |
| 0-100 time | L-Series | `getZeroToHundredValue`, accept greater than 0 and less than 25.3 else `--` | vehicle-controlled |
| Eighth-mile elapsed time | All | old listener supplies `setEighthEValue(String)`; L-Series `getEighthTimeValue`, accept greater than 0 and less than 25.3 else `--` | vehicle-controlled |
| Eighth-mile speed | All | old listener supplies `setEighthMphValue(String)`; L-Series `getEighthSpeedValue`, parse integer and accept 1 through 252 else `--` | vehicle-controlled |
| Quarter-mile elapsed time | All | old listener supplies `setQuaterEtValue(String)`; L-Series `getQuarterTimeValue`, accept greater than 0 and less than 25.3 else `--` | vehicle-controlled |
| Quarter-mile speed | All | old listener supplies `setQuaterMphValue(String)`; L-Series `getQuarterSpeedValue`, parse integer and accept 1 through 252 else `--` | vehicle-controlled |
| 60-foot elapsed time | L-Series | `getSixtyFeetValue`, accept greater than 0 and at most 5.0 else `--`; row gated by `_is60ftTimerAvailable` | vehicle-controlled |
| Braking distance | All | old listener supplies `setBrakeDistValue(String)`; L-Series `getBrakeDistValue`, parse integer/range check and apply its MPH-unit conversion; row gated by braking-label availability | vehicle-controlled |
| Braking speed | All | old listener supplies `setBrakeSpeedValue(String)`; L-Series `getBrakeSpeedValue`, parse integer and accept 1 through 252 else `--`; row gated with braking data | vehicle-controlled |

The old concrete Best, Current, and Last metric/US view listeners supply the stored strings through the listed base setters. L-Series consolidates the transfer in `CommonTimerView.updateTimerValueLabels()V`: reaction at BCI 1, 0-60 at 5, 0-100 at 9, eighth-mile pair at 13, quarter-mile pair at 17, conditional 60-foot at 28, and braking pair at 42. The generated report records every exported measurement as an individual field rather than treating all label text as one unexamined input.

## Variant row order

Viper/Jeep export this order:

1. 0-60 time.
2. Eighth-mile elapsed time.
3. Eighth-mile speed.
4. Quarter-mile elapsed time.
5. Quarter-mile speed.
6. Braking distance, only when `brakeDistLabel` is non-null.
7. Braking speed under the same braking-data branch.

L-Series export this order:

1. Reaction time.
2. 0-60 time.
3. 0-100 time.
4. Eighth-mile elapsed time.
5. Eighth-mile speed.
6. Quarter-mile elapsed time.
7. Quarter-mile speed.
8. 60-foot elapsed time when `_is60ftTimerAvailable` is true.
9. Braking distance when `_brakeDistLabel` is non-null.
10. Braking speed under the same braking-data branch.

The presence of a conditional row changes fixed structure selection; it does not admit markup or arbitrary field names.

## Encoding and escaping

**PROVED:** `TimerSavingData.updateHTML` opens `FileOutputStream(File)` at BCI 7, loads literal encoding name `UTF8` at BCI 16, constructs `OutputStreamWriter(OutputStream,String)` at BCI 18, calls `Writer.write(String)` at BCI 26, and `Writer.flush()` at BCI 31. It closes the underlying `FileOutputStream` at BCI 39 rather than closing the writer.

The consequences established by code are:

- UTF-8 is requested by Java encoding name; no BOM insertion is requested.
- The generated String contains no newline literals, and no newline-normalization operation is called.
- No HTML entity encoding or context-sensitive escaping is applied to dynamic text.
- The only final text transform is global `|` to `i` replacement.
- The meta element declares `text/html;charset=utf-8`; no separate MIME dispatch or HTTP header exists on the file path.
- No CSS, JavaScript, links, images, embedded resources, forms, or external resource references are emitted.

Unescaped strings do not by themselves prove controllable markup. The recovered producing sources are fixed resources, platform locale/time data, and vehicle-controlled numeric labels. No user-entered HTML source is recovered.

## Locale and resource boundary

Viper/Jeep package `timer_save_file_title`. L-Series `convertDataToHtml` requests that same key at BCI 82, but the recovered `common/localization.res` does not contain it and `use_shared_resources=false`. Its resource manager calls the external UI manager with an empty default. **UNKNOWN:** the exact resulting L-Series title text cannot be proved from its JAR alone; an empty title is plausible but is not promoted to a fact.

All 13 packaged L-Series timer-state locale values were decoded during the filename review; those values affect the basename, not the HTML body. Platform current/default locale tables used by `SimpleDateFormat`, including month and AM/PM data, remain an external runtime dependency.

## Failure boundary

`convertDataToHtml` does not catch runtime exceptions from label access, number preparation, timezone display-name substring, or resource behavior. `updateDialogAndButtons` also has no local catch around HTML/filename construction. **UNKNOWN:** an unchecked failure before `saveDataTo` has no reconstructed packaged 23/24 result UI. Once the writer is reached, open/write/flush checked failures are rethrown to status mapping, while close-only `IOException` is logged and suppressed; see [performance_pages_export_call_graph.md](performance_pages_export_call_graph.md) and the generated [failure signatures](../reports/kim19_runtime_analysis/performance_pages_export_failure_signatures.json).

## Static boundary

**PROVED:** this is a fixed application-owned report with platform- and vehicle-controlled text values. **INFERRED:** it supports Level 2 variable application-generated content, not arbitrary content. **UNKNOWN:** exact live values, locale fallback behavior, and L-Series missing-title behavior require external runtime evidence. No claim of HTML rendering or execution is made.
