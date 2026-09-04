# RA4 18.45.01 rollback and recovery design

## Status and purpose

This report defines the rollback contract for the minimal-change design in `reports/minimal_change_design.md`. It is a future design only. No head unit, firmware, application registry, marker, certificate, or update image was changed while producing it.

Rollback has four distinct meanings on RA4 and they must not be conflated:

1. remove one newly installed application;
2. return AMS from development to production security selection;
3. recover from inconsistent application state;
4. reinstall authenticated stock software after a serious failure.

Only the first two are candidates for the intended routine rollback, contingent on prior dynamic proof of per-app removal and continuing legitimate access to item 19. The fourth is disaster recovery. The recovered platform has no proved general transactional undo for either application installation or the 13-unit software-update sequence.

Evidence grades are `CONFIRMED`, `HIGH`, `DESIGN`, and `UNKNOWN` as defined in `reports/minimal_change_design.md`.

## Recovery objectives and non-negotiable invariants

The target rollback state is:

```text
custom app not running
custom app absent from AMS/AppManager inventory
custom app-owned data disposition explicitly verified
/fs/etfs/AMS_DEVELOPMENT absent
stock production security.jar selected at the next AMS start
AMS still launched with -secure
factory anti-theft behavior unchanged
/fs/etfs/enableEngMenu unchanged
stock update path and signed media unchanged
normal radio/HMI/audio/climate/update-service health verified
```

Rollback must never depend on bypassing service-certificate verification, entering or changing an anti-theft PIN, modifying a trust store, changing `/fs/etfs/enableEngMenu`, setting `/fs/etfs/disableDRM`, overwriting stock Xlet/Kona trees directly, or forging an update.

## Baseline evidence package

`DESIGN`: before any future mutation, create a read-only, unit-private baseline. It should contain:

- software version, model year/market/product, part number, and a timestamp;
- stock hashes for `jvm.sh`, production/development security JARs, AMS, AppManager, and the compatible owner-supplied update package;
- presence/absence of `/fs/etfs/AMS_DEVELOPMENT`, `/fs/etfs/disableDRM`, and the separate AppManager catalog gate `/fs/etfs/enableEngMenu`;
- the selected `jvm.sh` security path and confirmation that AMS uses `-secure`;
- installed application IDs, versions, signer/package information where exposed, running/paused state, and a separate list of factory/preload apps;
- the new custom app ID, signed-package hash, expected data directory, expected policy, and exact authorized signer fingerprint;
- for an external-media trial, hashes of the offered outer medium, authenticated nested installer ISO, approved `external.start_script`, and application package, recorded without treating outer-media mounting as nested-ISO authentication;
- update-in-progress/retry state, normal boot health, and stable-power arrangements;
- legitimate service-certificate validity window recorded privately without committing the certificate or HU serial.

Relevant stock identities include:

| Artifact | SHA-256 |
| --- | --- |
| `jvm.sh` | `9bd3c63a2c22c17f96e037102283f453afca43eb093bc1291d607a9805f829ec` |
| AMS | `96683b789ecf06a8575915d0b446b532e1f4ee87feb31d925cb7ba3d7d324d27` |
| production `security.jar` | `29a8a350ef0facc30c1c98e5250563a4020ad9c1a243f13e795e2e68e3bd74e7` |
| development `security.jar` | `fbe5314ab304e122162aae20ace46999b93832fc4c7451439f4ada430eccc8a7` |
| hidden-HBC AppManager | `608f45f96fa71bfe2c8a2566e973953d9de74ba7afa0cdd2e31cf408137c5591` |
| resident `swdlMediaDetect/loader.lua` | `f562650958dc487d8558571744cc517ba583550b29c79dba4f335fc07c47e885` |
| resident `swdlMediaDetect.lua` | `0bf54e5866ad0a8bff467e592e5ee46d877ba957ee6f1f266f7d94191001088c` |
| stock RA4 distribution ZIP | `5388d9310737dc52a65f2825131043362254b3592da2584302b81bc0447f9fdd` |
| `swdl.upd` | `c704eb723d6697fd98959888274dda18362c23ce6f66b505e01ce1983148c344` |

The baseline is evidence, not a raw filesystem backup to write back indiscriminately. AppManager's visible persistent list is now identified as the whole-value `AppManager_JavaApps` JSON record in the PersistentKeyValue/QDB `keyvalue` database, but AMS's own registry/filesystem commit and reconciliation rules remain unknown. Restoring copied directories or that JSON value behind AMS/AppManager could therefore make state less consistent.

## Routine rollback sequence

### R0 - no-mutation abort

If service-certificate validation fails, package metadata differs from approval, the signer is not recognized, permissions exceed the approved set, update state is non-idle, or stable power is unavailable, remove only the offered media/staging artifact through its stock owner and stop. Do not create the development marker and do not attempt an install.

This is the safest and preferred abort because it intends to leave no Development Security or application mutation. Verify the stock invalidation/cleanup result: the candidate service certificate is copied before evaluation, and its deletion behavior has been reconstructed statically rather than observed on hardware.

`CONFIRMED`: diagserv supplies another internal factory-oriented certificate path, but not transactional rollback. Routine `0xF010` stages the active `/etc/security/service.cert` with a truncating first write, appending continuations, and no temp/rename/fsync/backup; an open failure receives the same internal staging acknowledgment as success. Finalize separately invokes the platform evaluator, whose signature, HU-serial, and lifetime checks remain authoritative. Routine `0xF011` directly removes the path but does not clear already-published `service_flags` or notify the HMI, so immediate live revocation is unproved. Neither routine contains the external diagnostic-session/SecurityAccess gate, so no use is permitted until an authorized factory workflow, upstream gate, and supported state-refresh boundary are proved. HMI item 20 remains unrelated because it deletes `/fs/etfs/service.key` without calling diagserv.

### R1 - development marker selected, application not installed

While the same legitimate service authorization remains valid:

1. Re-enter the stock engineering Service menu.
2. Select `Enable Production Security` through item 19.
3. Independently verify `/fs/etfs/AMS_DEVELOPMENT` is absent.
4. Perform a normal controlled boot on stable power.
5. Verify `jvm.sh` line-61 output or equivalent process evidence selects `/fs/mmc1/kona/security/security.jar` and that `-secure` remains present.

The independent marker check is required. `AppsListEngServiceMenu::DevepSecurityKeyEnabled` catches and traces marker-creation move errors after changing UI state, and the delete branch does not expose a separate robust success result. The label alone is not a rollback proof.

If the service certificate expired before the marker could be removed, do not bypass menu authorization or write the marker directly. If an authorized issuer or service organization can provide a new legitimately issued, unit-bound certificate, use that stock route; otherwise remain stopped in the observed state and escalate to authorized service. No self-service production-return guarantee currently exists. This return-access requirement is a hard precondition to enabling development selection in the first place.

Do not use engineering-menu item 20 as a substitute certificate rollback. `AppsListEngServiceMenu::onItem` case 20 (`0x37D11`-`0x37D75`) directly deletes only `/fs/etfs/service.key`; it makes no Peripheral, ModuleLink, D-Bus, or platform-service call. The platform certificate is separately configured as `/etc/security/service.cert`, resolving under `/fs/mmc0`, and no alias, runtime relationship, or revocation edge between the two paths has been proved. `DELETE_SERVICE_KEY` is therefore outside the routine rollback sequence unless its separate consumer and effect are first established.

### R2 - application installed and healthy enough to manage

The intended order is:

1. After its runtime semantics have been dynamically demonstrated on disposable state, stop the custom app through the pre-validated stock lifecycle boundary.
2. Request uninstall of exactly its approved application ID through AMS/AppManager, using the pre-validated per-app boundary.
3. Query package/application state and confirm that ID is absent.
4. Confirm no process or Xlet state remains for that ID.
5. Verify `/fs/etfs/usr/var/appman/xletRMS/<appId>` and `/fs/etfs/usr/var/appman/xletRMS/common/<appId>.rs` are absent, then verify every additional package-documented data path; remove nothing directly.
6. Return to production security using R1.
7. Verify normal vehicle and update-service behavior.

This intended ordering retains the development acceptance context until removal is independently verified, then returns the global selector to production. The design does not grant the custom app permission to uninstall itself or manage other applications. Native per-app cleanup is now proved, but a returned success and the two known RMS deletions still do not establish atomic or exhaustive removal.

`CONFIRMED`: the stock application ecosystem exposes per-app removal. KIM3 `DeleteTask.class` invokes `uninstallApp`; `InstallHelper$InstallerImpl.class` contains `uninstallApp` and `installApp`; `AMSClient` contains command-form `remove`. In `kona.jar`, `AppManagerImpl.uninstallApp(String)` starts at class-file offset `0x2E8C`, checks `AppMgrPermission("appMgr")` at `0x2E95`, loads the `uninstallApp` SvcIPC operation at `0x2EBC`, and invokes the client at `0x2EC3`.

`CONFIRMED`: native AppManager (SHA-256 `608f45f96fa71bfe2c8a2566e973953d9de74ba7afa0cdd2e31cf408137c5591`) dispatches `uninstallApp` at file `0x54058` (VA `0x154058`) to `startUninstallApp` at VA `0x191158` (file `0x91158`). That routine stops the app if needed and reaches `uninstallNow` at VA `0x190FAC` (file `0x90FAC`). Async success reaches `onUninstalled` at VA `0x18FE94` (file `0x8FE94`), queues `finishUninstallation`, and the dispatcher at file `0x5CF74` invokes the finish routine at VA `0x193910` (file `0x93910`). The finish path calls `cleanUpXletResources` at VA `0x13B0CC` (file `0x3B0CC`) and queues `deleteAppFromHashMap`; the event loop at file `0x5C058` invokes handlers at VAs `0x156DFC` and `0x133C4C`.

`CONFIRMED`: `cleanUpXletResources` calls `removeRMSFiles` at VA `0x131B94` (file `0x31B94`). With `xletRMSDir=/fs/etfs/usr/var/appman/xletRMS`, it conditionally executes `rm -R` for `<xletRMSDir>/<appId>` and `rm` for `<xletRMSDir>/common/<appId>.rs`. Thus the success path removes per-app Xlet resources, its native map entry, its RMS directory, and its common `.rs` record.

`UNKNOWN`: atomicity across the stop, asynchronous uninstall, resource cleanup, RMS deletion, and map/list updates; the state that survives interruption; every application-owned path outside the two proved RMS targets; and restoration of a previous version. Therefore success requires post-operation inventory and data verification, not just a returned status. The design observes the native cleanup results and never runs its internal `rm` commands directly.

### Confirmed AppManager registry and transaction boundary

`CONFIRMED`: native AppManager persists its Java application inventory as one full JSON array under key `AppManager_JavaApps` (string file `0x101C54`). `readJavaAppsList` begins at VA `0x130050` / file `0x30050`. `saveJavaAppsList` begins at VA `0x157698` / file `0x57698`, issues a persistence `read` through `0x57704..0x577C0`, rebuilds the array from the native map at controller `+0xAC`, and issues a separate `write` through `0x58818..0x58858`. Its sole direct call is the event dispatcher at file `0x5C348`; no compare-and-swap value, generation number, transaction ID, retry loop, or transaction spanning both IPC calls was found.

`CONFIRMED`: unmatched PersistentKeyValue names use the `keyvalue` database (`pmem_keyvalue.ini:14-20`). `qdb.cfg:41-44` maps it to `/usr/var/qdb/key_value` with full validation and schema `/etc/sql/persistency_mgr/key_value.sql`; that schema defines `keyvalueTbl(key TEXT PRIMARY KEY,value TEXT NOT NULL)` and `PRAGMA journal_mode=truncate`. The backend performs a single SQL `UPDATE` with `INSERT OR REPLACE` fallback, while `qdb_backup` is a separate adapter call. The `keyvalue` section has no `Backup Dir`, and `qdb_recover.sh:21-22` handles detected corruption by deleting `key_value*`, not by restoring a configured backup.

`CONFIRMED`: this database update is not the AMS installation commit. After AMS success and native finish processing, `autoStartApp` emits `appListUpdated` at `0x91580..0x91584` and only then queues `saveJavaAppsList` at `0x91608..0x9160C`. Uninstall likewise crosses separate phases: the AMS response/signal handshake reaches `finishUninstall`, then resource/RMS cleanup, queued native-map deletion, `appListUpdated`, and finally a queued full-list write through `0x5C130..0x5C1C4`. An interruption can therefore leave AMS/filesystem, native-map, and QDB-list views at different generations.

`CONFIRMED`: AppManager's tracked resource helpers are also non-transactional. Temporary cleanup executes `rm %s` at file `0x8DE6C`, and installation resource movement executes `mv %s %s` at file `0x8DFC8`; both ignore `system()`'s result and unconditionally clear their tracking vectors. This can turn a partial move or failed deletion into untracked residual state.

`CONFIRMED OWNERSHIP / UNKNOWN SEMANTICS`: AMS `Installer.install(String)Application` owns the install rename diagnostic at body/load `0x5BFCC0/0x5BFD56`; `Installer.recoverProgIfNeeded(String)V` owns exact `prog.bak` at `0x5BFDFD`, loading it at `0x5BFE1B` and `0x5BFEE3`; and `Installer.upgrade(String)Application` owns both upgrade rename diagnostics at body/loads `0x5BFE8C/0x5BFF2E/0x5BFF5C`. This proves a real program-backup recovery facility. The triggering branch, parent path, restoration/deletion order, completeness, and power-loss guarantees remain unproved. See `reports/appmanager_registry_atomicity.md`.

### R3 - ambiguous or partially failed application install

The live media installer removes its staging file after an explicit `status=ok`, but no end-to-end A/B application slot or transaction journal spanning AMS, AppManager, resources, and QDB was found. KIM3 contains cleanup and delete-before-install behavior, not a proved backup of the old package. AMS does contain `prog.bak`/installation-directory rename vocabulary, but the owning branch and any restoration guarantee are unresolved. If power loss, timeout, or an ambiguous response occurs:

1. Do not repeat install/upgrade blindly.
2. Query package information for both the intended app ID/version and any prior version.
3. Query running/paused Xlet state and inspect only the app-owned staging/data locations.
4. If AppManager recognizes the new app and the per-app stop/uninstall semantics were dynamically demonstrated before the trial, use that pre-validated path once and verify removal; otherwise stop and escalate.
5. If AppManager recognizes the prior app and its signed package is available, do not overwrite it until the exact upgrade/reinstall semantics are proved.
6. If registry and filesystem views disagree, stop. Do not repair by copying or deleting files behind AMS/AppManager.
7. Keep or restore production security only through the stock item-19 path, according to the known marker state.
8. Escalate to an authorized service/recovery environment; treat an OEM-signed software update as disaster recovery, not a continuation of the failed install.

The failure is not made safer by `xletsReturnToNew`; that command is deliberately excluded for the reasons below.

## Why `xletsReturnToNew` is not rollback

The name can be mistaken for a lifecycle transition. The recovered native implementation proves otherwise.

`analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_00f20000/files/bin/appManager` is 1,268,061 bytes, HBC image offset `0xCF000`, SHA-256 `608f45f96fa71bfe2c8a2566e973953d9de74ba7afa0cdd2e31cf408137c5591`.

- `parseRequest` compares `xletsReturnToNew` at file offset `0x5C460` (VA `0x15C460`); the equal branch calls handler file offset `0x2AA7C` (VA `0x12AA7C`) via the branch-and-link at `0x5C4A8`.
- `xletsReset` is a different parser branch. It must not be conflated with `xletsReturnToNew`.
- handler `0x12AA7C` requests writable media, removes shared record-store files, removes record-store folders, removes Xlet installation folders, and removes `/fs/mmc1/resource` contents. Its diagnostics are at file offsets `0x101DDC`, `0x101E24`, `0x101E7C`, `0x101EC8`, and `0x101F1C`.
- helper `0x12A95C` restores preinstalled Xlets with a recursive copy, removes the AMS temporary folder, and requests a head-unit reset; diagnostics are at `0x101D04`, `0x101D5C`, and `0x101DA8`.
- reset helper `0x12A890` invokes `requestReset`.

The paths are configured by `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_00f20000/files/etc/system/config/appManager.cfg` (5,802 bytes, SHA-256 `ab9ed180574d2c9f83c45217f05b132af24abd364ecf59c8447d1ba0cdb9c2d7`): lines 8-10 define preload, installed-Xlet, and shared RMS locations.

`CONFIRMED`: `xletsReturnToNew` is a broad factory-application-state restoration followed by a complete head-unit reset. It can remove unrelated applications, shared RMS state, and resources. It is not scoped to the custom app, does not toggle `/fs/etfs/AMS_DEVELOPMENT`, and is not a developer-token operation.

The anti-theft HMI path sends this command after an entered-PIN transition to unlocked on relevant VP4 variants. That historical coupling does not make it a development authorization callback; it increases the risk of deliberately exercising the PIN path during application testing. A rollback plan must never intentionally trigger it.

## Returning AMS to production security

`CONFIRMED`: `jvm.sh` line 58 always initializes the production path; line 59 selects development only when `-f /fs/etfs/AMS_DEVELOPMENT` succeeds; line 63 passes the chosen JAR while retaining `-secure`.

`CONFIRMED` within the materialized/searchable scope: item 19 is the only located marker creator/deleter. Across 778 hidden-HBC regular files totaling 89,007,481 bytes, no additional `AMS_DEVELOPMENT` literal was found. The stock marker owner should therefore also own the candidate rollback path.

`CONFIRMED`: the marker is sampled at AMS process creation, not watched for immediate reload. `platform_ams_restart.lua` reacts to AMS service loss/startup timeout and reinvokes `jvm.sh`; it has no `AMS_DEVELOPMENT` string. It separately references `/fs/etfs/disableDRM`, which selects AppManager command text with or without `-d`. Native `appManager` does not register `drm/d` in the option set built at VA `0x196028`; a later normalized `drm` handler at `0x19718C` has no located registration path. The observed `-d` may therefore be ignored or dead/indirect and must not be used to infer or alter AMS security selection.

`CONFIRMED` and separate: native AppManager function file offset `0x29E08` tests `/fs/etfs/enableEngMenu`; its sole direct caller, `createEmbeddedApps` at `0x3D1C0`, uses it to retain or filter embedded application ID `engineering`. No writer was found. This embedded-application catalog gate is not service authorization, item 19, or `AMS_DEVELOPMENT`; rollback records but never changes it.

`DESIGN`: rollback uses a normal controlled boot after verified marker removal. It must not crash or kill AMS merely to accelerate selection. After boot, verify the production path explicitly. Merely deleting a file while the old AMS process remains alive does not change that process's loaded security configuration.

## Authenticated application media is ingress, not rollback

`CONFIRMED`: the resident `swdlMediaDetect/loader.lua` recognizes SWDL insertion at `usb0`, expects `swdl.upd`, mounts it at `/fs/swdl`, authenticates each present nested ISO, requires and mounts `installer.iso` at `/fs/installer`, and loads its manifest (`loader.lua:70-80,497-568`; 22,538 bytes; SHA-256 `f562650958dc487d8558571744cc517ba583550b29c79dba4f335fc07c47e885`). `swdlMediaDetect.lua::processManifest` dispatches `manifest.external.start_script`, and the loader supplies `ISO_PATH=/fs/swdl`, the detected `USB_PATH`, and `INSTALLERISO_PATH=/fs/installer` before running the selected script from the authenticated installer ISO (`swdlMediaDetect.lua:242-266`; `loader.lua:595-621`; dispatcher SHA-256 `0bf54e5866ad0a8bff467e592e5ee46d877ba957ee6f1f266f7d94191001088c`). The recognizer and environment handoff are no longer unknown.

This confirmed dispatch chain is not authority to construct media and provides no undo operation. The recovered `us-app-install.sh` consumes the exported `ISO_PATH` and `USB_PATH`, but the stock 18.45.01 manifest has no `external` member, so it does not prove the exact `external.start_script` value used by factory application media. The corpus also has neither a factory external-install manifest nor a sample application JAR below `usr/share/APPS`. A trial must stop unless an authorized issuer supplies a legitimately signed installer ISO with the approved external manifest and the complete live package schema is independently validated. The materialized `segment_001a0000/files/etc/keys/swdl.pub` is a 451-byte, 2,048-bit RSA public key with SHA-256 `804e7cdf410c74a2b6ac52084d9b24c7b5becfd5bbb66a32819356d01f5b676e`; it can verify a signature but cannot create or authorize one. Repacking the stock update or editing its manifest would cross the authenticated boundary and is prohibited.

## Signed software update is recovery, not transactional rollback

The stock USB update scripts define a strongly authenticated design. The three owner-supplied nested images now independently verify at the RSA header-signature and full-data-hash layers described below, but this does not dynamically validate the complete update state machine or make installation a proved transaction.

`analysis_ra4_18.45.01/work/installer_iso/usr/share/scripts/update/isochk.lua` is 9,509 bytes with SHA-256 `51b4777fa98e8a0f338336b2ebacd7cdccd9e1493817c76f3ef41cad33be2e9f`. Its main validation prototype, source/debug lines 170-392, is designed to verify the signed 32 KiB ISO header with RSA/SHA-256 using `/etc/keys/swdl.pub`, check product/market/model/downgrade constraints, verify the full ISO data hash and size, and authenticate install-monitor hash material. `install.sh` refuses copy/authentication failures and runs `installmonitor.lua` against the streamed secondary ISO. The public key is materialized at `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_001a0000/files/etc/keys/swdl.pub` (451 bytes; SHA-256 `804e7cdf410c74a2b6ac52084d9b24c7b5becfd5bbb66a32819356d01f5b676e`).

Fresh Node cryptography verification confirms all three stock nested images: each block-0 RSA-SHA256 signature verifies over header bytes 256-32,767, and public-decrypting block 127 produces the 32-byte digest that matches SHA-256 over bytes 32,768 through EOF. The matching data digests are installer `880561a00022ea658a211a76947abb2e2cef1882e64372c6209b3ec7ee7337c1`, primary `fd5e4ab6409eb6e583c7ccf82d0a7be08980a8b081677efc32f0b0fe94dbe5c6`, and secondary `22468c3ba91c125559f6269c444a5c32fa437c08cac8d4b304f55e8ec5761898`. This proves the header-signature and full-data-hash checks for the owner-supplied stock artifacts, not signing authority: the public key cannot generate or authorize a new installer image.

When correctly enforced, this design is intended to reject unauthorized package content; it does not make installation reversible.

`analysis_ra4_18.45.01/work/installer_iso/etc/manifest.lua` (SHA-256 `104d18836f41919f1f789110697eebc5e6deee998de79fb5a4c0af35a042770f`) defines 13 ordered units: system check, IOC bootloader, IOC, System, System Data, Speech, EQ, Apps, Embedded Air Card, XM pre-update, XM update, HD update, and OTA update. `softwareupdate.lua` persists unit/substate and can reset into a required mode to retry or resume. A later failure can therefore occur after earlier units were already written.

The specific rollback limitations are:

- resume/retry returns to an update unit; it does not undo prior successful units;
- no general A/B system slot, per-unit undo log, previous-IFS restore, or reverse-flash sequence was identified;
- `parseConfig.lua` understands `[backup]` and `[restore]`, but the stock materialized update configs contain no active sections using them;
- the only confirmed partition preservation is `MMC_TB` Take Back: `mmc.sh` lines 111-204, 488-499, and 598-600 temporarily copy `/fs/mmc1` to `/fs/mmc0/mmc1_bk` around repartition and restore it; this is not general application rollback;
- application install/upgrade has no proved previous-version restoration; AMS contains exact `prog.bak`/rename handling vocabulary, but its ordinary-upgrade trigger and restore semantics remain unknown;
- a stock update has not been proved to remove `/fs/etfs/AMS_DEVELOPMENT`; development-to-production return remains a separate required action.

`DESIGN`: retain an unmodified, compatible, OEM-signed stock update as candidate last-resort recovery media. Its exact-version/state acceptance and the authorized service procedure must be proved before relying on it. Use it only with stable power after ordinary per-app rollback is exhausted. Never repack it to carry the custom application. Never describe re-running it as an atomic rollback.

## Failure-response matrix

| Observed condition | Routine response | Prohibited response |
| --- | --- | --- |
| Service certificate rejected, serial mismatch, or expired | Stop before marker change; use reissuance only if an authorized issuer/service can provide it, otherwise escalate | Alter `scv`, certificate, serial, date checks, or public key |
| Diagnostic certificate staging reports success but file/completion state is ambiguous | Treat authorization as absent, preserve state, and stop for an authorized service workflow; a staging tuple is not validation | Retry segments blindly, invoke internal IPC directly, or assume the active certificate is intact |
| Item-19 label changes but marker state is unverified | Treat state as unknown; perform read-only marker check before boot | Assume label proves success |
| Development marker present, AMS still production | No app install; use a normal controlled boot and verify selection | Kill AMS/AppManager or set `disableDRM` |
| AMS starts development JAR but package preview fails | Do not install; remove marker through item 19 and return production | Edit package metadata or trust store |
| SWDL media or nested installer authentication fails, or the authenticated manifest has no approved `external.start_script` | Stop before package staging; remove only the offered medium through the stock owner | Repack the update, edit the manifest, bypass loader checks, or attempt to sign with the public verification key |
| Secure install returns explicit failure | Inspect package state once; if absent, remove staging and return production | Retry repeatedly or pass preview `auth=false` semantics to install |
| Secure install result is ambiguous | Follow R3 and stop on registry/filesystem disagreement | Directly edit `/fs/mmc1/xletsdir` or hidden registry state |
| Custom app crashes or harms HMI responsiveness | Stop/uninstall that app through stock lifecycle, then R1 | Use `xletsReturnToNew` as a quick reset |
| Service authorization expires while development is selected | Remain stopped; use a new unit-bound certificate only if an authorized issuer/service can provide it, otherwise escalate | Delete marker directly or bypass service flags |
| Normal per-app uninstall succeeds | Verify package/process absence, both known RMS targets, every documented app-owned path, and production return | Assume one success status or the two RMS deletions prove atomic or exhaustive cleanup |
| Unit cannot reach normal AppManager/AMS management | Stop, preserve logs/state, escalate to authorized recovery; signed update only as last resort | Broad deletion, unverified shell repair, or unsigned/repacked firmware |

## Recovery checkpoints

Each checkpoint has an explicit go/no-go result.

### Checkpoint A - before service authorization

Go only when stock hashes and current marker/update state match baseline, recovery-media integrity and exact-unit compatibility are verified with an authorized use procedure, and service-certificate validity is sufficient for the entire test and return. Otherwise stop with no mutation.

### Checkpoint B - after development selection, before boot

Go only when the marker is independently confirmed present, `/fs/etfs/disableDRM` and `/fs/etfs/enableEngMenu` are unchanged, and the production-return path remains available. Otherwise use item 19 to return to the baseline marker state before any boot if valid service authorization remains; if not, remain stopped and escalate.

### Checkpoint C - after boot, before install

Go only when the stock development JAR is the selected `-securityConfiguration`, AMS remains `-secure`, AppManager/AMS services are healthy, and all normal vehicle surfaces pass the baseline health check. Otherwise return production without installing.

### Checkpoint D - after authenticated media dispatch and package preview, before install

Go only when the resident loader has accepted the nested installer signature/hash, its authenticated manifest selected the approved external script, and app ID, version, Kona compatibility, authorized signer, signed member set, developer credential status, and least-privilege policy exactly match the approved off-unit record. Otherwise remove only offered media/staging state through its stock owner and return production.

### Checkpoint E - after install

Go only when exactly one new app ID appears, the expected version and policy are reported, normal vehicle health is unchanged, and no unexpected change appears within the explicitly baselined and monitored scope. Otherwise invoke R2 or R3 according to whether AppManager recognizes the app.

### Checkpoint F - closure

Closure requires: application absent, known RMS targets absent, every documented owned-data path handled, marker absent, `/fs/etfs/enableEngMenu` unchanged, production JAR selected after a normal boot, AMS `-secure`, stock hashes unchanged, no update in progress, normal vehicle health, and stock update media still verifiable.

## Power-loss and interruption rules

Power loss is most dangerous between an authenticated mutation and its post-check. The design therefore permits only one state transition between checkpoints:

1. service certificate accepted;
2. marker toggled;
3. controlled boot completed;
4. one package installed;
5. one package removed;
6. marker removed;
7. controlled production boot completed.

Never combine marker selection, package upgrade, and firmware update in one trial. Never begin while the vehicle can be driven. Use stable bench/maintenance power appropriate to the head unit and stop if voltage or thermal state is abnormal.

After an interruption, resume from observation, not from the last intended action: read current marker, selected AMS path, AMS/package inventory, AppManager catalog/map view, persistent `AppManager_JavaApps` view through its stock owner, process state, and update state before choosing R1, R2, or R3. Any disagreement is a stop condition; do not repair the QDB value or application directories directly.

## Preserving stock firmware-update capability

The routine design is intended to minimize risk to update capability; actual post-change acceptance and operation still require verification:

- no stock ISO, `swdl.upd`, manifest, installer script, application/KIM tree, or signature is modified;
- no update public key, service public key, Kona trust file, or system executable is changed;
- the custom application is installed through the live AMS path, not injected into a firmware image;
- production security is restored and verified before a stock software update;
- the custom application is uninstalled before update unless an official compatibility/provisioning rule explicitly permits it;
- the marker's ETFS state is handled separately rather than assuming either reboot persistence or signed-update removal without observation;
- the original signed update and its hashes remain offline and read-only.

The full update's Apps unit may repopulate Xlets from factory/KIM content, but that is not a safe one-app rollback and may affect all application state. Recovered `qkcp` proves why: its `-h` option is only shared-memory progress, the KIM caller passes no `-f/-r` checkpoint recovery, and the copier creates/truncates final destinations directly without rename/remove rollback. A failed factory population can leave mixed or partial state (`reports/qkcp_kim_copy_semantics.md`). Its existence does not justify skipping the per-app uninstall and production-return proof.

## What remains unresolved before implementation

The rollback design is not ready to execute until all of these are closed:

1. a legitimately issued, stock-valid external installer manifest/media set, plus the exact live application package schema and official/authorized packaging tool;
2. exact native developer signer, principal, token, and policy-acceptance rules;
3. exhaustive per-app uninstall disposition for the AMS-installed payload, AMS-internal registry, and application-owned paths beyond the confirmed AppManager map/QDB-list update, resource cleanup, and two RMS targets;
4. exact AMS `prog.bak`/rename ownership and restore/delete flow, AMS-to-AppManager boot reconciliation, QDB durability settings, and install/upgrade behavior after power loss at each stage;
5. a read-only runtime method to verify marker state and selected security configuration on the target unit;
6. a legitimate service-certificate issuance and renewal path that guarantees production-return access, including any official external diagnostic route plus its session/SecurityAccess gate and interruption recovery;
7. unit-specific authorized recovery behavior if AppManager/AMS cannot reach a manageable state;
8. proof that the chosen compatible signed stock update is accepted in the unit's exact version/state and a documented service procedure for using it.

Any unresolved item remains a stop gate. Recovery media is not a substitute for understanding the mutation that precedes it.

## Evidence references

- `reports/authorization_bridge_deep_dive.md` - exact `xletsReturnToNew` receiver/effects, service-certificate chain, and AMS restart behavior.
- `reports/service_certificate_diagnostic_transport.md` - diagserv certificate staging/removal, platform validation boundary, external-gate unknowns, and non-atomic interruption behavior.
- `reports/qnx_boot_filesystems.md` - recovered boot/HBC artifacts and hashes.
- `reports/developer_mode_ui.md` - item 19 marker owner and error behavior.
- `reports/application_install_pipeline.md` - install, upgrade, uninstall, lifecycle, and atomicity gaps.
- `reports/appmanager_registry_atomicity.md` - `AppManager_JavaApps` persistence, QDB backend, lifecycle ordering, resource failure handling, and AMS backup bounds.
- `reports/kona_application_authorization.md` - signed package, AppManager permission, and native trust gaps.
- `reports/usb_update_pipeline.md` - signed ISO validation, unit sequencing, resume/retry, and absence of general rollback.
- `reports/security_jar_diff.md` - stock production/development configuration identity.

## Repository and evidence safety

Before every commit:

```text
Stock/vendor firmware staged: NO
Owner-specific certificate or serial staged: NO
Private key, anti-theft PIN, authentication key, or raw developer token staged: NO
```

The decoded HBC filesystems, stock binary/JAR/ISO contents, service certificate, and vendor signing material must remain ignored and unstaged. This report may be committed because it is original research prose containing only paths, structural evidence, offsets, and hashes.
