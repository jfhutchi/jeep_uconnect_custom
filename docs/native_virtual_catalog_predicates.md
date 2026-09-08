# Native virtual catalog predicates

**PROVED:** this analysis is limited to recovered `appManager` SHA-256
`608f45f96fa71bfe2c8a2566e973953d9de74ba7afa0cdd2e31cf408137c5591`.
The catalog function begins at VA `0x124dcc`; the targeted branch is
`0x12592c..0x125980`. ARM virtual addresses in this document subtract
`0x100000` to obtain file offsets. No target state is read.

## Recovered decision

The tree node at `r4` holds a `CAppManagerBaseApp *` at `+0x10`. The function
loads its vtable and calls selectors `0x10`, `0x0c`, and conditionally `0x18`.
It then reads the cached byte at app offset `0x4d`. **PROVED:** the entry reaches
the append path only when:

```text
!headless && (!daemon || hasGUI) && showInHmi
```

| Site | Input and resolved implementation | Consumer | Role |
|---|---|---|---|
| `0x12592c..0x125940` | candidate `r0`; vtable selector `0x10`; `CAppManagerApp` implementation `0x10bcbc` returns byte `app+0x284` | true branches to skip at `0x125b44` | **PROVED:** headless exclusion |
| `0x125944..0x125958` | same candidate; selector `0x0c`; implementation `0x10bcf4` returns byte `app+0x239` | false bypasses the next test | **PROVED:** daemon qualifier |
| `0x12595c..0x125970` | same candidate; selector `0x18`; implementation `0x10bc4c` returns byte `app+0x295` | false branches to skip, but only for a daemon | **PROVED:** daemon `hasGUI` exception |
| `0x125974..0x125980` | same candidate; direct byte `app+0x4d` | false branches to skip | **PROVED:** cached `showInHmi` gate |

**PROVED:** the `CAppManagerApp` RTTI object is at `0x200004` and names
`14CAppManagerApp`; the base RTTI object at `0x2014bc` names
`18CAppManagerBaseApp`. The installed `CAppManagerApp` vtable has its RTTI word
at `0x1fffbc`. From the object vptr at `0x1fffc0`, selectors `0x0c`, `0x10`, and
`0x18` resolve to `0x10bcf4`, `0x10bcbc`, and `0x10bc4c`. Those functions
return `app+0x239`, `app+0x284`, and `app+0x295`, respectively.

**PROVED:** the property vocabulary in the same binary contains `xlet.daemon`,
`xlet.headless`, and `xlet.hasGUI`. The response vocabulary contains `daemon`
and `hasGUI`. The internal VSBClient construction path at `0x1608d0` sets
`app+0x239`, and at `0x1608d8` sets `app+0x284`; it is a daemon/headless stock
service. These independent definitions bind the three getter roles above.
The abstract base implementations at `0x11f598`, `0x11f568`, and `0x11f508`
return false and do not change the concrete mapping.

**PROVED, exact parser dataflow:** `extractProperties` loads `xlet.daemon` at
`0x1d0218..0x1d0244` and stores the parsed byte to property offset `+0x19d` at
`0x1d0268`. When true it loads `xlet.hasGUI` at `0x1d0280..0x1d02b4` and stores
to `+0x1f9` at `0x1d02e0`; the false-daemon/default branch also stores that
field at `0x1d0348`. It then loads `xlet.headless` at
`0x1d034c..0x1d0380` and stores to `+0x1e8` at `0x1d03b8`. The property
subobject begins at app offset `0x9c`, so those addresses resolve exactly to
`app+0x239`, `app+0x295`, and `app+0x284`.

## Affected catalog views

**PROVED:** the same selector sequence appears in three branches of
`getAppListByHmiCategory`:

| Category branch | Predicate sites | Additional condition |
|---|---|---|
| category value `-1` | `0x124e38`, `0x124e58`, `0x124e70` | byte `app+0x4c` must also be true before the virtual tests |
| enumerated category values `1..6` | `0x125618`, `0x125634`, `0x125650` | candidate category must match the requested category |
| remaining/default category branch | `0x125938`, `0x125950`, `0x125968` | no additional Yelp-specific predicate precedes the trio |

**PROVED:** the `-3` branch at `0x1250a4` is structurally different. It performs
`__dynamic_cast(CAppManagerBaseApp, CAppManagerApp)`, checks application state
and visibility, and builds the running list. It must not be described as using
the exact targeted predicate trio.

## Yelp implications

**PROVED:** recovered Yelp `xlet.properties` declares `xlet.daemon=false` and
does not declare `xlet.headless=true`. **INFERRED:** for a matching installed
Yelp object, the daemon/GUI part should reduce to the ordinary non-daemon path.
Its catalog exposure still depends on the object being present in the native
map, the requested category/view, the headless field being false, and
`showInHmi` being true.

**UNKNOWN:** the current radio's installed object, field values, catalog
freshness, and category request. These predicates do not name Yelp, a region,
an account, a subscription, or a DRM grant. **PROVED:** manual launch applies a
separate DRM-enabled `findAndStartApp` path after catalog rendering. Therefore:

- **INFERRED:** absent from every recorded page is compatible with missing
  registration, headless or `showInHmi` filtering, category state, or stale data.
- **UNKNOWN:** absence alone cannot identify which predicate failed and cannot
  establish uninstall, expired subscription, or failed launch authorization.
- **INFERRED:** a disabled or non-launching visible tile has already crossed
  these catalog inclusion checks, so investigation moves to HMI enabled state,
  native start, AMS, and Xlet lifecycle.
- **TARGET OBSERVATION REQUIRED:** record the complete catalog scope and exact
  tile styling before assigning outcome A or B.

The reviewed predicate records are stored in
[the observation model](../analysis_tools/yelp_observation_model.json). The
[launch-gate model](yelp_launch_gate_model.md) keeps these catalog predicates
separate from later authorization and service gates.
