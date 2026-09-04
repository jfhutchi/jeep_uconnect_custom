# RA4 `qkcp` and KIM Copy Semantics

## Scope and safety

This report closes the earlier question of what `qkcp -h` does in the RA4 18.45.01 factory Xlet/KIM installer and what state may remain after a failed copy. All conclusions are static and apply to the exact recovered RA4 binary identified below. No vendor executable was run, no stock image was modified, and no recovered command is presented as an installation procedure.

## Artifact provenance

The sole recovered executable is:

- path: `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_001a0000/files/bin/qkcp`;
- inventory: `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_001a0000/inventory.tsv:120`;
- size: 50,222 bytes;
- SHA-256: `aa5605bdd69581aad74c05213553ccac2468399de18f539cf1c2029d58207198`;
- format: little-endian ARM ELF32 `ET_EXEC`, entry VA `0x1021C8`;
- `main`: VA `0x1047FC`, file offset `0x47FC`, size `0x1C64`;
- QNX build description: `quick copy utility using DirectIO method`, version `650-4608`, build `2017/04/05-14:28:12-EDT`.

The complete owner-media provenance is:

| Layer | Bytes | SHA-256 |
| --- | ---: | --- |
| `Uconnect_VP4,18.45.01-My13-17.zip` | 1,266,203,571 | `5388d9310737dc52a65f2825131043362254b3592da2584302b81bc0447f9fdd` |
| `analysis_ra4_18.45.01/extracted/swdl.upd` | 1,426,147,328 | `c704eb723d6697fd98959888274dda18362c23ce6f66b505e01ce1983148c344` |
| `analysis_ra4_18.45.01/work/swdl_iso/primary.iso` | 375,191,552 | `8086b7b6a413c9fd2718d21bd7d027c79c0dc36a1e1d43ea1f7358fd33b890ff` |
| `analysis_ra4_18.45.01/work/primary_iso/usr/share/IFS/ifs-cmc.bin` | 42,122,670 | `ea6797be141763f35f3059ad858eefbf54f730af0155bebc7af411c47d80ba92` |
| decoded HBC imagefs at `0x001A0000` | 30,909,752 | `996c5a52cf7e72bb73d95e34e684196ca702061c6c5d9977415b014fbea57fbb` |
| decoded image `bin/qkcp` at `0x003F0000` | 50,222 | `aa5605bdd69581aad74c05213553ccac2468399de18f539cf1c2029d58207198` |

An independent in-memory decode with `analysis_tools/qnx_ifs_inventory.py` confirmed the HBC header at parent offset `0x001A0000`, compressed region `0x001A0040..0x00F0CCDA`, 14,077,083 compressed bytes in 472 QNX-framed LZO blocks, the decoded-image hash, and the `qkcp` offset/size/hash. The outer ZIP has five direct members and no direct `qkcp` member. No second exact executable was found in the standard imagefs, the other HBC inventories, or the local UAS comparison corpus.

## `-h` is progress reporting, not a hash manifest

**[CONFIRMED]** The earlier theory that `qkcp -h` authenticates `xletsdir_ref.txt` is false for this binary.

The non-loaded `QNX_usage` section is at file offset `0xAA53`, size 2,493, SHA-256 `9c6afe5bda92bc04c566b6f166fe6316458bdfee6dfbc79fb7804c4294b739be`. It describes `-h shname` as using `/dev/shmem/shname` for copy progress.

Native control flow agrees:

1. The getopt string `b:viVWrsc:f:h:S:O:X:m:` is at file offset `0x9BF4`.
2. The `h` jump-table entry at file `0x498C` reaches VA `0x104B3C` / file `0x4B3C` and stores `optarg` at configuration offset `+0xE0`.
3. The consumer at VA `0x105A38` / file `0x5A38` normalizes a leading slash and calls `shm_open(name, O_RDWR)` at VAs `0x105A78..0x105A88`.
4. It calls `ftruncate64(..., 0x38)` at VAs `0x105AA0..0x105AB0`, maps the object shared at `0x105AC0..0x105AE8`, and zeroes all 56 bytes at `0x105B1C..0x105B54`.
5. The fatal path writes the final status at mapped offset `+0x30` at VAs `0x1035E0..0x1035F4`.

The 56-byte mapping matches the embedded progress fields: job/completed bytes, file counts, times, percentage, phase, and status. It is not a manifest buffer.

The factory caller is `analysis_ra4_18.45.01/work/installer_iso/usr/share/scripts/update/installer/xlets.lua`, 8,006 bytes, SHA-256 `e6849b1260417cdc89762ae76cac1b0f01bab28a833d2211b80498ae0d4466cc`. Its decoded constants show:

- `rm -f /tmp/` at bytecode-string offset `0x1BBF`;
- `;touch /tmp/` at `0x1BD0`;
- `qkcp -h ` at `0x1BE2`;
- the status `/tmp/` path at `0x1C33` and final removal at `0x1E1E`;
- the reader builds `cp <object> /tmp/temp_file` from `0x0693/0x069C`, then opens the temporary file in binary mode at `0x06C6/0x06EC`.

`xlets.lua` passes no `-f`, `-r`, or `-X`, and contains no MD5 or `xletsdir_ref` command constant. The executable contains no manifest filename, `xletsdir_ref` string, payload-hash/crypto import, or parser for the KIM MD5/length record format. Its optional `-X dll[:argument]` callback surface is unused by this caller. A corpus-wide static search found `xletsdir_ref.txt` only as KIM data/inventory entries, not as an executing consumer.

**Boundary:** The KIM `xletsdir_ref.txt` files do contain MD5, length, and destination triples, but `qkcp` does not enforce them. The already-proved signed nested ISO is the confirmed integrity boundary for the factory source bytes. A dynamically constructed or unrecovered later consumer cannot be excluded, but none is evidenced in the recovered RA4 or UAS corpus.

## Copy and failure semantics

**[CONFIRMED]** `qkcp` performs a source-driven recursive merge/overwrite. It is not a mirror, atomic transaction, or rollback mechanism.

- `main` calls `nftw64(source, callback VA 0x106460, ..., flags 0xC)` at VAs `0x105EEC..0x105F04`.
- The regular-file callback at VAs `0x10661C..0x10665C` calls the copy routine at VA `0x104100` and propagates a nonzero result; `main` treats nonzero traversal completion as fatal at `0x105F08..0x105F18`.
- The copy routine opens the source at VA `0x1041BC` and calls destination creation at VA `0x102AF8`.
- Destination creation passes the final destination path directly to QNX `_connect` at VAs `0x102C08..0x102C18`; there is no temporary sibling path.
- When lengths differ, the final destination is resized to the source length with `ftruncate64` at `0x104218..0x104268` before payload copying.
- Destination metadata is sent at `0x1042F0..0x1043E4`, then the data copier at VA `0x1037A4` is called from `0x104480..0x1044C0`.
- Error branches close descriptors at `0x104508..0x1045B8`, but do not restore or remove the destination.

Dynamic imports include `_connect`, `open`, `open64`, `ftruncate64`, `MsgSend`, `read`, `write`, `pwrite64`, `lseek64`, `fsync`, `close`, `mkdir`, `nftw64`, `shm_open`, and `mmap64`. There is no `rename`, `unlink`, `remove`, or `rmdir` import.

Those facts establish the following failure boundary:

- a new destination can remain empty, pre-sized, or partially populated;
- an existing destination can contain old and newly overwritten regions;
- metadata can change before copying fails;
- entries copied earlier in traversal remain;
- destination-only entries remain because this is a merge, not a mirror;
- no previous version is snapshotted or restored; and
- no temporary-tree rename commits the operation atomically.

The KIM caller increases the risk because it removes selected working/preload content before issuing replacement copies. A recognized copy failure can therefore leave an incomplete or mixed KIM tree.

## Checkpoint behavior

`qkcp` checkpoint recovery is independent of `-h`:

- `-f` names a checkpoint file;
- `-r` enables recovery and requires `-f`;
- `-c` controls checkpoint spacing;
- `-h` only publishes progress.

The embedded status table identifies `0` success, `1` generic failure, `2` graceful signal shutdown with updated checkpoint, `3` corrupt checkpoint, `4` read error, `5` write error, `6` corrupt filesystem, `7` no space, and `14` checkpoint source/destination mismatch. The string `Checkpoint file corrupt - cksum` at file `0x9E28` describes checkpoint-file integrity, not payload authentication.

The recovery branch at VAs `0x104608..0x1047F8` reopens the existing source/destination and resumes the same copier from saved offsets. On failure it closes descriptors but does not delete, restore, or rename the destination. The signal thread at VA `0x104064` uses the fatal `qkcp interrupted by signal` path without a checkpoint and status `2` / `qkcp stopped gracefully` with one. Because KIM passes neither `-f` nor `-r`, its `-h` invocation has progress but no `qkcp` checkpoint/resume protection.

## Installation and rollback implications

1. `xletsdir_ref.txt` must not be described as a `qkcp`-enforced authorization layer.
2. The signed software-update container authenticates factory input, but authenticated input does not make the multi-file destination mutation atomic.
3. Factory KIM population is not a safe one-app installation or rollback surface. It can pre-delete and then non-atomically merge broad Xlet/preload state.
4. A failed factory application-unit copy requires observation of the entire affected Xlet/preload tree; repeating the update blindly can compound mixed state.
5. The safe custom-app design remains the stock live AMS per-application path, contingent on its own still-unresolved package schema, signer authorization, registry atomicity, and rollback gates.

## Static-analysis limits

The current evidence does not establish private QNX `_connect` metadata-field semantics, every DirectIO retry/fallback, traversal order on every filesystem, which optional `fsync` policy is active, filesystem-journal power-loss durability, checkpoint-file crash consistency, or an unknown consumer outside the recovered corpus. It also does not establish an atomic relationship among KIM file copying, AMS registry state, and native AppManager state.

These limits do not change the central result: the recovered KIM use of `qkcp -h` is a monitored, non-atomic directory merge/overwrite with no proved manifest verification or built-in rollback.
