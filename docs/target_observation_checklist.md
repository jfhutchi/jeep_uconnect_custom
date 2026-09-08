# Ordinary Apps observation checklist

**TARGET OBSERVATION REQUIRED:** this is a future observation procedure. The
radio has not been contacted or operated during this static research phase.
Use ordinary visible menus only, while safely parked. Do not enter hidden menus,
diagnostics, registration/payment flows, ASSIST calls, vehicle controls or settings
that change configuration.

**PROVED from recovered code:** opening/launching an app can update launch
history, running state, RMS or preferences and can initiate normal service
requests. Therefore a normal launch is a limited observation, not a guarantee
of zero state changes. Do not repeatedly launch apps to reproduce a symptom.

## Record the catalog first

1. Record date/time, displayed language, and the ordinary screen/menu used.
   Record software/version only if already exposed by an ordinary information
   page; do not hunt through hidden menus.
2. Photograph or record every Apps page and each ordinary category, including
   All Apps. Capture Favorites/Running separately if available. Avoid duplicate
   interpretation of an app appearing in more than one category.
3. Transcribe exact names, page/category, position/order, icon and greyed/disabled
   appearance. Include entries outside the nine KIM19 names. Record whether the
   list changes during the initial survey. Do not reorder favorites or change
   categories' contents.
4. Record existing network/account/service banners and running indicators
   exactly. A grey tile is an observation, not proof of a DRM failure. Order may
   depend on category, language, name or recent start time.

| Page/category | Position | Exact name | Icon description | Grey/disabled? | Running indicator | Existing message |
|---|---|---|---|---|---|---|
| | | | | | | |

## Single highest-value launch

**INFERRED priority:** if Yelp is present, make **one normal Yelp launch attempt**
after recording the catalog. This most directly tests the remaining boundary
between a returned entry and working stock-signed UI.

Record the tap time and, without additional actions, the first screen, whether
a Yelp splash appears, approximate elapsed time, subsequent home/loading/error
screen, exact title/message/buttons, immediate return to Apps, and whether it
stays visible or is reported running. A short continuous recording is preferable
to a single late screenshot because it preserves a brief splash/error.

Do not dismiss a prompt that would register, subscribe, purchase, agree to new
terms, place a call or change state. Do not select a result's call/navigation
action. If nothing progresses after a reasonable observation interval (for
example 30 seconds), record that interval and stop; do not retry or reset.

If Yelp is absent, the single useful next observation is the completed Apps
inventory itself; **do not substitute an ASSIST, Store or Register launch**.
No search is needed for this first pass. If an ordinary search was already
performed, record the existing outcome and exact query/result relationship
without repeating it for the research.

| One-attempt record | Value |
|---|---|
| Yelp page/category, initial icon/running state | |
| Tap time; first visible screen | |
| Splash appeared? Approximate duration? | |
| Home/search UI appeared? | |
| Exact error title/body/buttons | |
| Returned immediately? Approximate elapsed time? | |
| Stayed visible/running? For how long observed? | |
| Account/network/service message already shown | |
| Any unavoidable normal history/preference change noticed | |

## Interpret the record

These claims apply **after** the observation is actually supplied.

| Observation | Evidence established | Still unresolved |
|---|---|---|
| Yelp absent from complete survey | PROVED no exposed Yelp entry at that moment | UNKNOWN installed/registered state, filters, flags, authorization |
| Yelp tile, launch fails | PROVED catalog exposure and visible failure | UNKNOWN native authorization versus AMS/init/UI cause |
| Yelp splash | PROVED app-branded UI execution; INFERRED recovered init/scheduling path crossed | UNKNOWN fresh start versus resume, exact JAR, network/backend |
| Yelp home/search | PROVED usable first UI | UNKNOWN search/connectivity/backend success |
| Generic search/application error | PROVED displayed message | UNKNOWN whether any network response arrived |
| Response-specific backend error | INFERRED response parsing, if matched to recovered error.id branch | UNKNOWN backend identity, credential validity, failure cause |
| Fresh relevant search results | INFERRED successful request/response/parse/display operation | UNKNOWN arbitrary inbound capability/listener |
| Register present | PROVED Register catalog entry | UNKNOWN subscriber stage; presence does not mean unregistered |
| Register absent | PROVED not exposed in surveyed views | UNKNOWN registration completion versus another catalog gate |
| Store absent/present | PROVED catalog observation | UNKNOWN account, backend, launch DRM |
| ASSIST present | PROVED exposed entry | UNKNOWN current subscription, calling or VSB state |
| Performance Pages | PROVED same-named entry; INFERRED one variant exposed | UNKNOWN exact variant/flags/PPS and launch authorization |
| VSBClient/DRMSync absent | PROVED no foreground entry | UNKNOWN headless service activity |
| App in Running view | INFERRED HMI/AppManager running-state report | UNKNOWN current responsiveness or successful service operation |

**UNKNOWN:** even a Jeep-branded Performance screen does not retrospectively
prove every catalog predicate or launcher-mask bit. Valid parsing sets the native
condition flag, but current installed descriptors, retained conditions and PPS
remain unobserved; the three packages share a display name.
Use the [runtime model](kim19_runtime_observation_model.md) for the precise
conditional interpretation and [Yelp cases A-F](kim19_yelp_reachability.md) for
the most informative next classification.
