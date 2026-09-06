# Portable projection arbiter core

Original C99 candidate for the RA4-resident integration layer. It mirrors the
version-2 ownership semantics in `prototype/resident_hmi/model.mjs` without a
browser, JavaScript runtime, heap allocation, filesystem, networking, graphics,
audio, vehicle transport or vendor API.

This is not a radio application and has no loading/install mechanism. An eventual
stock AIR screen, native QNX process or narrow bridge may call equivalent logic
only after its lifecycle and ABI are established. The adapter remains responsible
for translating proved stock events into complete snapshots.

Host conformance build when a C compiler is available:

```text
cc -std=c99 -Wall -Wextra -Werror -pedantic projection_arbiter.c test_projection_arbiter.c -o projection_arbiter_test
./projection_arbiter_test
```

The implementation has a compile-time `sizeof(PA_Arbiter) <= 128` guard. It uses
only C99 `stdbool.h` and `stdint.h`; the test alone uses `assert.h` and
`stdio.h`. No target binary has been built or measured yet.

Resource targets for this component:

| Item | Planning target | Measured |
| --- | ---: | ---: |
| Compiled code and read-only data | <=64 KiB | UNKNOWN |
| Arbiter state object | <=128 bytes compile-time guard | UNKNOWN |
| Heap allocation | 0 bytes by design | Not runtime-verified |
| Persistent/log/cache writes | 0 bytes by design | Not runtime-verified |
| Standalone update/temp space | 0; packaged inside the bounded trial | UNKNOWN |

The full projection integration still follows the 15 MB installed, 4 MB writable,
8 MB additional peak and 45 MB protected-reserve envelope. The projection engine,
video, touch, USB and audio adapters are deliberately not hidden in this core.
