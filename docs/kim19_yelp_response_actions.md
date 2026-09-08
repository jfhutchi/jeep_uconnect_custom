# KIM19 Yelp response actions

The field-to-sink ledger is [response_actions.json](../reports/kim19_yelp/response_actions.json).

## Search response

| JSON field | Required? | Stock sink |
|---|---:|---|
| `error.id` | conditional | `ERROR`, service-unavailable dialog |
| `total` | yes on non-error | string `0` selects `Zero_Results` |
| `businesses[]` | yes for results | `ArrayList<Place>` and result screen |
| `name`, `rating`, `review_count` | yes per item | result/details text and rating/review UI |
| `phone` | optional | call button -> `Phone.dial(String)` |
| `RestaurantsPriceRange2` | optional | local price-level display |
| `hours` | optional | period model and open-hours dialog |
| `distance` | optional | display; otherwise local coordinate distance can be calculated |
| `location.display_address` | yes | result/details address text |
| `location.address`, `city`, `state_code`, `country_code` | yes | Place region fields and navigation Geocode |
| `id` | yes | Place reference; no executable dispatch |
| `categories` | optional | category model/labels |
| `location.coordinate.latitude/longitude` | yes | Place doubles, distance, navigation destination |

**PROVED:** many fields are accessed without `has` checks. A malformed business
can throw during the whole parse rather than being skipped. Optional fields are
guarded where noted. Coordinates that cannot be used become 0.0 in the parser's
fallback branch.

Results route to screen 71 on 8.4/default and 75 on 6.5. Selecting a business
builds a map for screen 72 details. Details render packaged images and LWUIT
labels/buttons; no remote image URL is consumed.

**PROVED scoped negative:** response strings reach model setters, labels,
distance/geocode logic, phone, and navigation. They do not reach a WebView,
HTML/JavaScript parser, shell/process launcher, class loader, media player, or
SocketCommandSource. This rejects an executable-content interpretation of the
legacy JSON response within the recovered Yelp code.
