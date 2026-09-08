# KIM19 Yelp input dataflow

The canonical flows are in [input_dataflow.json](../reports/kim19_yelp/input_dataflow.json).

## Touchscreen search

1. **PROVED:** the 8.4 home constructs `SearchFieldContainer` and a voice button.
2. **PROVED:** pointer release checks vehicle lockout outside the emulator.
3. **PROVED:** `launchGpKeyboard` first calls `GpGeoUtil.isLocationValid`; invalid
   location produces a local GPS alert and returns.
4. **PROVED:** keyboard OK rejects a concurrent search, empty text, text
   containing the localized search hint, and exact hint text.
5. **PROVED:** `CVPKeyboardTextInput.getText` at BCI 190 supplies the exact
   string to `GpUtil.setSearchName`, `setSearchTerm`, and the
   `GpSearchRequest(dialog,text,"0")` constructor at BCI 227. There is no trim
   at this boundary.
6. **PROVED:** `ConnectionManager.addRequest` at BCI 234 enqueues it; the spinner
   blocks the caller-visible flow until cancel/completion.

Ordinary text has apostrophes removed, is UTF-8 form-URL-encoded, and becomes
`term`. Text whose lower-cased value contains the localized `near` or `in`
token takes a special grammar: split at the first token, trim both sides,
remove `[$&+,:;=?@#|'<>./\-^*()%!]`, then encode term and location separately.
Spaces survive as URL-encoding output (normally `+`). **PROVED:** no command
interpreter, template processor, HTML engine, WebView, JavaScript engine, or
dynamic loader consumes the text before the HTTP request.

**UNKNOWN:** Yelp never calls `TextField.setMaxSize`; the exact LWUIT runtime
default is outside this Yelp binary. **STRONGLY SUPPORTED:** packaged keyboard
layouts include Latin letters, digits, space, common punctuation, accented
Latin characters, `.com`, and emoticons. Constant presence does not prove every
key/mode is reachable on every screen configuration.

## Voice search

1. **PROVED:** voice action checks location, then a worker calls
   `VRHelper.requestOffBoardVr`.
2. **PROVED:** `VRHelperImp.init` obtains the current locale and supported speech
   services. When the first service is secure it configures host/port and fixed
   bundled service material; all sensitive values remain omitted from reports.
3. **PROVED:** it obtains a session, installs state and recognition listeners,
   uses locale-specific `offboard*.eco`/`search*.eco`, and starts a background
   queue loop.
4. **PROVED:** the soft-button event requests a VR session; state logic starts
   offboard recognition. A recognized localized cancel word cancels. Any other
   recognized string is delivered by `Display.callSerially` to
   `SpeechListener.onVRAction`.
5. **PROVED:** `SpeechListener` stores the same string, constructs the same
   `GpSearchRequest` with sort `0`, and uses the same status/result screens as
   touch.

The platform speech service and its remote recognition path are real receiver
edges, but actual service availability and recognition are **TARGET OBSERVATION
REQUIRED**.

## Persistence and negative surfaces

**PROVED:** startup loads and destroy saves `9YelpPreDefItemRS`,
`9YelpPreSortRS`, and `9YelpUserSortRS`. They store category visibility/order
and user-defined search labels using `|`-separated records/maps. RMS failures
are locally printed/logged. The home favorite button only displays “function
currently not available”; no persisted POI favorite sink was found.

**PROVED scoped negative:** the complete Yelp JAR class/reference census found
no SocketCommandSource, CommandLooper, browser/WebView, HTML/JavaScript engine,
process launch, VSB/SDP client, media-launch API, or arbitrary class-loading sink.

