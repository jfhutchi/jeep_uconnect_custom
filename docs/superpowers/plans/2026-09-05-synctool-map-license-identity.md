# Synctool Map-License Identity Analysis: Plan and Closure

Date: 2026-09-05.

## Objective and boundaries

Determine how the 2017Q2 VP4 Synctool derives application identity and filters
a multi-variant license package, including the successful MY14 REVA case.
Analyze local vendor evidence read-only; publish only original tools, tests,
addresses, hashes, and non-secret derived metadata. Do not derive credentials,
license masks, activation values, signing material or a bypass.

This is a research closure record, not a claim that the exact MY14 numerical
record mapping has been observed. Detailed evidence and remaining inputs are
in reports/synctool_device_license_selection.md.

## Completed evidence-backed subgoals

- [x] Establish the ELF hash, size, entry point and mapped segments; protect
  ignored local firmware, recovery helpers, and the original image.
- [x] Build and test a reusable ELF32/ARM inspector. Cover mapped bounds,
  ARM/Thumb callers, embedded-data interruptions, literal addressing,
  immediate/field candidates, and truncated-disassembly reporting.
- [x] Recover the caller around 0x0011ACD0, its seventh-argument byte flag,
  the parent context field, singleton construction, and manager registration.
- [x] Resolve manager slot +0x58 and the Application distributor's concrete
  secondary interface. Trace selector 0x284 to encoded module 0x42000284,
  matching-record ranking, metadata +8, and the context +0x24 log.
- [x] Correct the input-SWID hypothesis: application_skuid is a property output
  populated by a query with selector 0 (substituted 6/7), not the pointer
  passed through [fp-0xA0]. Keep device.nng appcid distinct.
- [x] Trace scanner metadata +0x10 through both record accessors, the concrete
  record, loader, container constructor, and source-identity map allocation.
  Identify it as a runtime container ordinal, not App SKU or model-year ID.
- [x] Follow result flags and both scanner callers into invalid/activatable
  list pruning, container-wide record removal, source-name collection, and
  callback 0x00113160 clearing matching entries from the file-copy plan.
- [x] Qualify enum interpretation: constructors initialize discard-policy
  bytes; raw invalid records need not make the returned enum invalid.
- [x] Search ELF/media configuration for a MY14/REVA literal mapping and
  distinguish database/product compatibility from numeric license identity.
- [x] Search the entire 16,034,824,192-byte original image for intact diagnostic
  markers, then separately search the recovered 1,043,885-byte outer log.
  Only embedded format strings were found in the image; no outer-log hits.
- [x] Add a hash-gated 51-anchor verifier and a streaming diagnostic-marker
  probe. Keep output limited to safe static facts or marker metadata.
- [x] Update the main report, add the focused pipeline report, and link the
  reusable tools and findings from the repository README.
- [x] Verify all 80 analysis-tool tests and all 51 real-ELF anchors. Resolve
  the existing suite's missing cryptography dependency in an ignored local
  test directory, without changing the system Python package installation.

## Research outcome and remaining input

The generic classification-to-filename-exclusion mechanism is established.
The successful outer log identifies MY14 REVA, but does not provide that
file's numeric SKU or per-record states. No direct App-SKU-to-MY14 filename
lookup has been found. The initial proposed direct device.nng/SWID-to-SKU
pipeline is superseded by the proved license-record-to-property direction.

The remaining requirement is case-specific evidence, not a missing ELF
disassembler or unresolved App-SKU virtual call: an existing diagnostic trace
or legitimate non-secret installed-license inventory from the relevant radio
that correlates module/SKU, record validity, and the final filename plan.
The exact marker search cannot exclude compressed, fragmented or damaged
messages, or diagnostics stored only on the radio. No dedicated diagnostic
filename has been assumed.

Further credential derivation, payload decoding into reusable license
material, firmware execution/modification, and flashing are cancelled as
out of scope. The approved handoff is to commit and push the verified safe
text/tool artifacts on the current branch; the final response records the
actual commit and push result.
