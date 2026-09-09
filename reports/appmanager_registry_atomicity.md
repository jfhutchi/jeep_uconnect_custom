# RA4 18.45.01 AppManager Registry and Atomicity Trace

## Scope and method

This report traces the recovered RA4 18.45.01 native AppManager application-list persistence and the boundaries between AMS install/uninstall completion, AppManager's in-memory map, persistent key/value storage, and application-owned resource moves. It is a static, read-only analysis. No vendor executable was run, no firmware or application package was installed, and no stock artifact was changed.

The native binaries are stripped. Function names in this report such as `readJavaAppsList`, `finishInstall`, and `onUninstalled` are research labels recovered from event and diagnostic vocabulary; every material claim is anchored to a file offset or virtual address.

Evidence labels are:

- **[CONFIRMED]** Directly present in a recovered artifact or a bounded static call edge.
- **[CONFIRMED ABSENCE]** A named, bounded artifact or call-path census lacks the stated item; it is not a corpus-global impossibility claim.
- **[HIGH]** Supported by multiple static facts, but dependent on a closed runtime or filesystem boundary.
- **[INFERRED]** The best explanation of visible evidence, with plausible alternatives remaining.
- **[UNKNOWN]** Not established by the recovered corpus.

This report does not describe a security bypass. It does not weaken AMS, Kona, DRM, signer validation, the factory anti-theft PIN, or the signed software-update path.

## Artifact ledger

The ARM executables in this table map their first load segment so that the offsets discussed below use `VA = file offset + 0x100000` unless a different mapping is stated.

| Artifact | Size | SHA-256 |
| --- | ---: | --- |
| `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_00f20000/files/bin/appManager` | 1,268,061 | `608f45f96fa71bfe2c8a2566e973953d9de74ba7afa0cdd2e31cf408137c5591` |
| `analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/bin/AMS` | 11,956,352 | `96683b789ecf06a8575915d0b446b532e1f4ee87feb31d925cb7ba3d7d324d27` |
| `analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/bin/AMSClient` | 3,593,200 | `12439c3e2554d388c43ca7f1023e96ad2183f5ae22a20991041b833eaa4eec9e` |
| `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_001a0000/files/usr/bin/persistency_mgr` | 238,188 | `b5cdc69ac0dee1381980c965b9b5baec28a268627b78d26a77213e562a849f73` |
| `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_001a0000/files/usr/lib/libPmKeyValue.so.1` | 61,389 | `b47315b3baa2d1e08ebff023c9347ec1d187afb432d9378eb95681333199352f` |
| `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_001a0000/files/etc/persistency_mgr/pmem_keyvalue.ini` | 277,308 | `6e553c209b0277fa9b96fa8e2f77a4afb04d14b288222acac9f8814a8b928d1a` |
| `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_00f20000/files/etc/sql/persistency_mgr/key_value.sql` | 357 | `f4f532b8138df902e9a44f05a0f22fc60909e7981cb78852f08f1deac3f62285` |
| `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_00f20000/files/etc/qdb.cfg` | 970 | `24f4939ff8bf629a7194eb5ae827e9e8acca928ef40b02f30cb859e286f831e3` |
| `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_00f20000/files/etc/system/config/appManager.cfg` | 5,802 | `ab9ed180574d2c9f83c45217f05b132af24abd364ecf59c8447d1ba0cdb9c2d7` |
| `analysis_ra4_18.45.01/work/hidden_hbc_ifs/segment_00f20000/files/bin/qdb_recover.sh` | 1,401 | `d1782aa84aab78c9e5057d280ceb4f399e8d29fbc289bdd3a1f19f13aa6cb8db` |

The relevant AppManager storage roots are configured in `appManager.cfg`:

- line 8: `preloadXletsDir` is `/fs/mmc1/kona/preload`;
- line 9: `xletsDir` is `/fs/mmc1/xletsdir`;
- line 10: `xletRMSDir` is `/fs/etfs/usr/var/appman/xletRMS`;
- line 13: live DRM is `/fs/mmc1/kona/data/DRM.jar`;
- line 14: restore DRM is `/fs/mmc1/kona/preload/DRM.jar`.

## Persistent keys and service boundary

**[CONFIRMED]** AppManager initializes four named persistent objects:

| Key | File offset | VA | Initialization reference |
| --- | ---: | ---: | ---: |
| `AppManager_Favorites` | `0x101C3C` | `0x201C3C` | `0x2A6E8..0x2A6EC` |
| `AppManager_JavaApps` | `0x101C54` | `0x201C54` | `0x2A714..0x2A718` |
| `AppManager_RecentList` | `0x101C68` | `0x201C68` | `0x2A738..0x2A73C` |
| `AppManager_Registration` | `0x101C80` | `0x201C80` | `0x2A75C..0x2A760` |

The service and object strings are:

- `com.harman.service.PersistentKeyValue`: AppManager file `0x11588C`, VA `0x21588C`;
- `/com/harman/service/PersistentKeyValue`: AppManager file `0x1158B4`, VA `0x2158B4`;
- AppManager's service/object table references are at `0xB82F4..0xB831C`;
- JSON request field `key` is file `0x102530`, VA `0x202530`;
- response field `res` is file `0x1025A8`, VA `0x2025A8`;
- operation strings include `read` at file `0x112D4C`, VA `0x212D4C`, and `write` at file `0x1024C4`, VA `0x2024C4`.

The provider library independently exposes the same interface. `libPmKeyValue.so.1` contains `KeyValue` at file `0xCB84`, the service name at `0xCBD8`, the object path at `0xCC00`, and operations `read`, `write`, `delete`, and `commit` at files `0xCCF0`, `0xCCF8`, `0xCD10`, and `0xCD2C` respectively.

## JavaApps full-list load

**[CONFIRMED]** The loader labeled `readJavaAppsList` begins at AppManager VA `0x130050`, file `0x30050`.

1. It constructs a JSON request whose `key` value comes from controller field `+0x78`, the initialized `AppManager_JavaApps` key. Relevant construction spans `0x30090..0x3011C`.
2. It selects the persistence singleton at VA `0x16D160`, takes virtual slot `+0x1C` at files `0x30100..0x30104`, constructs operation `read` at `0x3010C..0x30110`, and makes the indirect call at `0x30138`.
3. Service-read failure branches at file `0x30150`, logs through the failure path at `0x30998`, and returns false.
4. A successful response is parsed from `res` at files `0x301F0..0x301F4` as an array. Per-entry fields are `appId` at `0x3031C..0x30320`, `appName` at `0x30384..0x30388`, and `medName` at `0x303EC..0x303F0`.

Diagnostic strings anchor the parser behavior:

| Meaning | File offset |
| --- | ---: |
| read start | `0x10358C` |
| entry count | `0x1035A4` |
| object added | `0x1035E8` |
| malformed object | `0x10361C` |
| response is not an array | `0x10365C` |
| parsing | `0x103690` |
| persistence read failed | `0x1036C0` |
| JSON exception | `0x1036F8` |

## JavaApps full-list save

**[CONFIRMED]** The writer labeled `saveJavaAppsList` begins at VA `0x157698`, file `0x57698`. It is not a per-application database update.

1. Controller byte `+0x4C5` gates persistence at file `0x576C8`. A false value logs through string file `0x109D44` and exits.
2. The writer first issues an independent `read` of the current value. Request construction is at `0x57704..0x57798`, operation construction is at `0x5778C..0x57790`, and the indirect service call is at `0x577C0`.
3. It parses the existing `res` value, then reaches the “write new list” diagnostic at file `0x109E88`, loaded at code `0x582D4..0x582D8`.
4. It walks the current native application map rooted at controller `+0xAC` and constructs a fresh JSON array. The walk begins around file `0x582E8`.
5. It logs the new count and serialized value through strings at files `0x109EB0` and `0x109EE0`, loaded at `0x5877C..0x58780` and `0x587AC..0x587B0`.
6. It constructs another request with the same persistent key, selects operation `write` at `0x5882C..0x58830`, and invokes the service at `0x58858`.
7. A zero/failure result branches at `0x588A0..0x588A4` to diagnostic file `0x109F10`. The writer then cleans native temporaries and returns by file `0x58A48`; it does not schedule a retry.

Additional writer diagnostics are at `0x109D2C` (entry), `0x109D7C` (existing count), `0x109DAC` (malformed object), `0x109DEC` (not an array), `0x109E20` (parse), `0x109E50` (read failure), and `0x109F4C` (JSON exception).

**[CONFIRMED]** The only direct call to the writer is dispatcher file `0x5C348`. The dispatcher compares the `readJavaAppsList` event at `0x5C2BC` and calls the loader at `0x5C2E0`; it compares `saveJavaAppsList` at `0x5C318`, sets `+0x4C5` at `0x5C33C..0x5C340`, and calls the writer at `0x5C348`.

Save events are queued by several lifecycle paths rather than writing synchronously at their mutation point:

- install finalization queues `saveJavaAppsList` at `0x91608..0x9160C`;
- post-uninstall map deletion queues it through `0x5C150..0x5C1C4` when `+0x4C5` is true;
- the bounded VR/state path at file `0x52184` also queues it when its state equals 3 and persistence is enabled.

**[CONFIRMED]** The initial `read` and later whole-value `write` are separate PersistentKeyValue calls. No caller-side compare-and-swap value, generation number, transaction ID, journal record, or retry loop was found. Even if the service makes each SQL statement atomic, AppManager's read/rebuild/write sequence is not one transaction with AMS filesystem mutation.

## PersistentKeyValue and QDB backend

`pmem_keyvalue.ini` explains the default disposition:

- lines 14-16 state that unmatched key/value names are stored in a database file located in ETFS;
- line 17 sets `"def_dbase" : "keyvalue"`;
- line 20 sets `"def_store" : "database"`.

**[CONFIRMED ABSENCE]** The file contains no explicit definition for any of the four `AppManager_*` keys, so the default database rule applies to them.

`qdb.cfg:41-44` defines the backend:

```ini
[keyvalue]
Validation Level = full
Filename        = /usr/var/qdb/key_value
Base Schema     = /etc/sql/persistency_mgr/key_value.sql
```

There is no `Backup Dir` entry in the `[keyvalue]` section.

The schema at `key_value.sql` contains:

- line 2: `BEGIN TRANSACTION;`
- line 9: `PRAGMA journal_mode=truncate;`
- line 13: `CREATE TABLE keyvalueTbl (`
- line 14: `key TEXT PRIMARY KEY,`
- line 15: `value TEXT NOT NULL`
- line 18: `COMMIT;`

The visible `BEGIN` and `COMMIT` delimit schema initialization. They do not prove that runtime AppManager reads and writes are grouped into a shared transaction.

The recovered `persistency_mgr` binds that schema to QDB:

- `/dev/qdb/keyvalue`: file `0x33598`, VA `0x133598`; references through literal pools at `0x18904` and `0x18B54`, loaded at code files `0x187C8` and `0x18A18`;
- `keyvalueTbl`: file `0x33874`, loaded at `0x1AD78`;
- `SELECT value FROM `: file `0x338C8`, loaded at `0x1B188`;
- ` WHERE key = '`: file `0x338DC`;
- `UPDATE `: file `0x338F0`, loaded at `0x1B5C0`;
- ` SET value = '`: file `0x338F8`;
- `' WHERE key = '`: file `0x33908`, loaded at `0x1B620`;
- `DELETE FROM `: file `0x33918`, loaded at `0x1B284`;
- `INSERT OR REPLACE INTO `: file `0x33934`, loaded at `0x1B760`;
- ` VALUES('`: file `0x3394C`, loaded at `0x1B788`.

The runtime builder first constructs an `UPDATE` at `0x1B5C0..0x1B648`, then an `INSERT OR REPLACE` fallback at `0x1B760..0x1B7DC`. The constructed statement is dispatched through the database handler at file `0x1B864`.

`qdb_statement` is dynamic symbol 50, PLT VA `0x102D04`, file `0x2D04`; the QDB adapter calls it at file `0x2853C` and checks result/row-change state. `qdb_backup` is separate dynamic symbol 140, PLT VA `0x103040`, file `0x3040`; its only direct call is file `0x2A158` in the separate backup adapter. AppManager sends operation `write`, not the separate PersistentKeyValue `commit` operation.

**[HIGH]** A JavaApps list update is therefore one JSON value submitted through one SQL `UPDATE` or fallback `INSERT OR REPLACE` statement. The configured truncate journal supports statement recovery, but the static corpus does not expose QDB's synchronous setting, filesystem flush ordering, or guaranteed sudden-power-loss durability.

### Corruption recovery

**[CONFIRMED]** `qdb_recover.sh` does not restore a configured key/value backup. On key-value corruption it logs `Deleting /usr/var/qdb/key_value*` at line 21, executes `rm -f /usr/var/qdb/key_value*` at line 22, and resets the unit at lines 41-42. The wildcard includes the database and possible sidecar files. The resulting AppManager-list reconstruction behavior after reset is **[UNKNOWN]**.

## Install completion ordering

The relevant research-labeled function boundaries are:

| Function | File range / entry |
| --- | --- |
| `onUpgraded` | `0x9029C..0x90628` |
| `onInstallStopped` | `0x90AAC..0x90FAC` |
| `autoStartApp` | entry `0x9147C`, VA `0x19147C` |
| `installNow` | entry `0x91AB4`, VA `0x191AB4` |
| `finishInstall` | entry `0x935BC`, VA `0x1935BC` |
| AMS `onInstalled` signal handler | entry `0x938A8`, VA `0x1938A8` |

**[CONFIRMED]** `installNow` calls AMS adapter VA `0x10EA84` at file `0x91C40`, passing callback `onUpgraded`, VA `0x19029C`, assembled at `0x91C38..0x91C3C`.

If the adapter call cannot start, the path logs through file `0x111690`, maps/answers the error at `0x91CC4..0x91CD4`, clears application install flag `+0x2AD` at `0x91CD8..0x91CE8`, changes intermediate state to 5 at `0x91CEC..0x91CF4`, and invokes restart handling. No registry save is made on that immediate failure path.

In `onUpgraded`:

- response status 3 logs the unreleased-write-permission condition through file `0x110F48` and answers with the bounded error path at `0x90410..0x90420`;
- other nonzero responses are mapped at `0x90434..0x90438` and answered at `0x9043C..0x9044C`;
- errors clear `+0x2AD`, set state 5, and invoke restart/autostart handling at `0x904C4..0x904EC`;
- response status 0 logs the indirect finish message through file `0x110FC0` and queues `finishInstallation` at `0x90508..0x905A0`.

The AMS `onInstalled` signal handler sets controller flag `+0x45` at `0x938D8..0x938DC` and calls `finishInstall` at `0x938E4`. `finishInstall` requires the installation state and `+0x45`, clears that flag at `0x93618..0x9361C`, updates the app through helper VA `0x10E008` at `0x936EC`, clears `+0x2AD`, sets state 5, moves tracked post-install resources, revokes write access at `0x93850`, and calls `autoStartApp` at `0x93858`.

`autoStartApp` emits `appListUpdated` through code `0x91580..0x91584`, then constructs and queues `saveJavaAppsList` at `0x91608..0x9160C`, before its later autostart decisions.

The confirmed native ordering is:

```text
AMS install/upgrade request
  -> successful AMS response and installed signal coordination
  -> finishInstall updates native application state
  -> move tracked post-install resources
  -> revoke write access
  -> autoStartApp / appListUpdated
  -> queue saveJavaAppsList
  -> dispatcher performs full JSON read/rebuild/write
```

**[CONFIRMED]** The AppManager persistent list write is after AMS completion signaling. It is not the AMS package commit point and is not a prerequisite for the AMS success response.

## Uninstall completion ordering

Relevant boundaries are:

| Function | File range / entry |
| --- | --- |
| `onUninstalled` | `0x8FE94..0x9029C` |
| `onUninstallStopped` | `0x90628..0x90AAC` |
| `uninstallNow` | entry `0x90FAC`, VA `0x190FAC` |
| `finishUninstall` | entry `0x93910`, VA `0x193910` |
| AMS `onUninstalled` signal handler | entry `0x93B40`, VA `0x193B40` |
| `deleteUninstalledApps` | entry `0x56DFC`, VA `0x156DFC` |

**[CONFIRMED]** `uninstallNow` stops the app as required, obtains write access, and calls AMS adapter VA `0x10E854` at file `0x910B0`. Callback `onUninstalled`, VA `0x18FE94`, is assembled at `0x910A8..0x910AC`. Immediate failure logs through file `0x1112B0`, answers the request, and clears uninstall flag `+0x2AE` at `0x9111C..0x91120`.

On a successful response, `onUninstalled` logs the indirect-finish path through file `0x110ED0`, loaded at `0x9016C..0x90170`, and queues `finishUninstallation` using token file `0x10AB3C`, loaded at `0x9017C..0x90180`.

The signal handler at `0x93B40` calls `finishUninstall` at `0x93B74`. `finishUninstall` uses controller byte `+0x46` as a two-event handshake. On the first event it logs “Still waiting for signal or response” through file `0x111D28`, sets `+0x46` at `0x9397C..0x93980`, and returns. When both sides have completed, it:

1. revokes write access at `0x9398C`;
2. resolves the application and logs completion through file `0x111D64`, loaded at `0x939F0..0x939F4`;
3. invokes the application uninstall-completion helper VA `0x10DF58` at `0x93A00`;
4. clears `+0x2AE` at `0x93A04..0x93A08`;
5. calls `cleanUpXletResources`, VA `0x13B0CC`, at `0x93A14`;
6. constructs and queues `deleteAppFromHashMap` at `0x93A24..0x93A84`.

The dispatcher recognizes `deleteAppFromHashMap` through string file `0x10A800` at `0x5C058..0x5C05C` and calls `deleteUninstalledApps` at `0x5C080`. That helper walks the native map rooted at controller `+0xAC`, erases/deletes matching objects, and decrements size field `+0xB0`. Its diagnostics include “delete app with appId” at file `0x109CAC`, loaded at `0x56E34..0x56E38`, and “no app” at file `0x109CF0`, loaded at `0x57610..0x57614`.

After map deletion, the dispatcher invokes a follow-up helper at `0x5C088`, emits `appListUpdated` at `0x5C098..0x5C0CC`, and, if `+0x4C5` is true, constructs and queues `saveJavaAppsList` through `0x5C130..0x5C1C4`.

The confirmed ordering is:

```text
AMS uninstall request
  -> AMS response/signal two-event handshake
  -> finishUninstall
  -> resource/RMS cleanup helper
  -> queue native-map deletion
  -> native-map deletion
  -> appListUpdated
  -> queue saveJavaAppsList
  -> dispatcher performs full JSON read/rebuild/write
```

No single transaction spans AMS payload mutation, cleanup, native-map deletion, and PersistentKeyValue storage.

## Resource move/delete non-atomicity

### Temporary resource deletion

**[CONFIRMED]** `answerRequest`, VA `0x18FD58`, file `0x8FD58`, always calls `deleteAllTempResources`, VA `0x18DDC4`, file `0x8DDC4`, at code file `0x8FDD8`.

`deleteAllTempResources`:

- logs through file `0x110B90`, loaded at `0x8DE08..0x8DE0C`;
- formats `rm %s` using string file `0x103B50`, loaded at `0x8DE14..0x8DE18`;
- loops through the in-memory vector and calls `system` PLT VA `0x1083E0`, file `0x83E0`, at code file `0x8DE6C`;
- does not test the shell command's return value;
- unconditionally destroys and clears the tracked vector at `0x8DEA0..0x8DEF4`.

### Post-install resource movement

**[CONFIRMED]** `finishInstall` calls the resource-move helper at VA `0x18DF38`, file `0x8DF38`, from code `0x93758`. It constructs destination `<xletsDir>/xlets/<appId>/data/`, formats `mv %s %s` through string file `0x110BB8`, loaded at `0x8DF84..0x8DF88`, and calls `system` at `0x8DFC8` for each tracked resource.

The helper does not test `system`'s result. It advances the loop and unconditionally clears the vector at `0x8DFCC..0x8E04C`. A partial or failed move can therefore become untracked within AppManager; no local retry record or rollback operation is visible.

### Filesystem primitive census

AppManager imports `open` at PLT VA `0x1083B0`, `system` at `0x1083E0`, `remove` at `0x108494`, `mkdir` at `0x1084F4`, `opendir` at `0x1085D8`, `read` at `0x10868C`, `access` at `0x108728`, `fopen` at `0x108800`, `write` at `0x1088A8`, `closedir` at `0x1088E4`, and `readdir` at `0x108D64`.

**[CONFIRMED ABSENCE]** Its dynamic import table contains no `rename`, `renameat`, `unlink`, `unlinkat`, `rmdir`, `fsync`, `fdatasync`, `sync`, `truncate`, `ftruncate`, `link`, `symlink`, `sqlite3_open`, or `sqlite3_exec`. This does not exclude operations performed through `system`, AMS, or statically linked code.

### Separate `/fs/mmc1/apps` deletion service

The request parser has a separate `getAppsFolderSize` branch: it compares that command at file `0x53734`, opens `/fs/mmc1/apps` through string file `0x10972C`, and formats `du -ps /fs/mmc1/apps/` through file `0x10973C`.

A distinct `deleteDir` branch compares its command at `0x53AF4`, parses `dirName` at `0x53B64` and `0x53C04`, formats `rm -R /fs/mmc1/apps/%s` through string file `0x109790` loaded at `0x53D04`, and calls `system` at `0x53D14`.

**[CONFIRMED ABSENCE]** No static call edge connects that externally requested branch to `finishUninstall`, `deleteUninstalledApps`, or the `/fs/mmc1/xletsdir/xlets/<appId>` package directory.

## AMS temporary directory and backup/rename vocabulary

### AppManager-created AMS temporary root

`createAMSTmpFolder`, VA `0x16D71C`, file `0x6D71C`, formats `%s/tmp/` through string file `0x10B694`, loaded at `0x6D758..0x6D75C`, using configured `xletsDir`. If absent, it obtains `/fs/mmc1` write permission, formats `mkdir %s` through file `0x10B724`, calls `system` at `0x6D7FC`, and checks only whether `system` returned `-1`. Its bounded caller at file `0x6BC44` is guarded as a startup/once operation.

This proves creation of `/fs/mmc1/xletsdir/tmp/`. It does not establish whether the directory holds an incoming archive, extracted staging tree, current version, or prior version.

The return-to-new flow around file `0x2A890` is separate from normal install/upgrade. It logs restoration of preinstalled xlets through file `0x101D04`, executes `cp -cpR %s/xlets/ %s/xlets/` through string file `0x101D40`, and removes `%s/tmp` with `rm -R %s/tmp` through file `0x101D98` before reset. This is factory/preload restoration, not proof of a per-upgrade backup.

### AMS AOT evidence

The recovered AMS executable contains one continuous tag-driven Jamaica name/descriptor pool from file `0x9C2071` through terminator `0xAB8ECC`: 60,877 entries, 1,011,292 inclusive bytes, SHA-256 `3663f3ee68908e0625de021a53537f33264786fb350e54b8fd5614786ed888fb`. The earlier fixed-26 anchor interpretation is superseded; tags encode full resets, front-coded entries, or extended full entries, while 26 is only the maximum reset gap. Complete relevant entries are:

| Complete decoded entry | Entry header / suffix start | Entry VA |
| --- | --- | ---: |
| ` is not present and neither is its backup` | `0x9D4C8E` / `0x9D4C90` | `0xAD4C8E` |
| `install failed to rename installation directory as '` | `0xA7FC03` / `0xA7FC05` | `0xB7FC03` |
| `prog.bak` | `0xA90B90` / `0xA90B92` | `0xB90B90` |
| `upgrade failed to rename installation directory as '` | `0xA9F339` / `0xA9F33B` | `0xB9F339` |
| `upgrade failed to rename new installation directory as '` | `0xA9F368` / `0xA9F36A` | `0xB9F368` |

The AMS dynamic-string area also contains import name `rename` at file `0x3A75`.

The install block also contains `install` at `0xA7FBC8`, failed-create diagnostics for the data and jars directories at `0xA7FBCD`/`0xA7FBF1`, and failed properties storage at `0xA7FC27`. The upgrade block contains `upgrade` at `0xA9F332`.

Class-pointer bounds, self-name markers, the global member-selector table, and embedded compact selector markers now establish direct ownership:

| Owner and method | Selector record | Class-object body/marker | Direct literal loads |
| --- | ---: | ---: | --- |
| `Installer.install(String)Application` | `0xAD7BE8` | `0x5BFCC0` | installation-directory rename failure at `0x5BFD56` -> pool entry `0xA7FC03` |
| `Installer.recoverProgIfNeeded(String)V` | `0xAD7BF0` | `0x5BFDFD` | `prog.bak` at `0x5BFE1B` and `0x5BFEE3`; missing/backup diagnostic at `0x5BFE42` |
| `Installer.upgrade(String)Application` | `0xAD7CA8` | `0x5BFE8C` | upgrade rename diagnostics at `0x5BFF2E` and `0x5BFF5C` -> pool entries `0xA9F339` and `0xA9F368` |

The `Installer` class is pointer-table slot 376, bounded file `[0x5BF5A8,0x5C0B88)`, with self-name marker at `0x5BF8E3`. This changes the claim from string-neighborhood inference to confirmed class/method attribution. The bytes at `0xA9F337` and `0xA9F366` are trailing bytes of preceding entries and are not valid headers.

**[CONFIRMED]** AMS `Installer` contains separate install/upgrade installation-directory rename paths, a dedicated `recoverProgIfNeeded` method that consumes exact `prog.bak`, a backup-presence diagnostic, and the imported `rename` primitive. A blanket conclusion that no installation backup exists anywhere in AMS is wrong.

**[CONFIRMED]** Full Installer bytecode reconstruction proves `prog.bak` is a sibling of `<appId>/prog`. Upgrade reconciles backup state, renames current `prog` to `prog.bak`, promotes staged `prog`, and deletes backup/staging after success. Recovery restores the backup only when `prog` is absent. See `reports/resident_incoming_jar_schema.md`.

**[UNKNOWN]** The recovered ownership and literal-load edges do not yet prove:

- whether `recoverProgIfNeeded` runs for every normal upgrade, only recovery, or another install mode;
- filesystem durability and the boot-time call reachability of normal recovery;
- whether the `.bak` directory is always a complete prior application version;
- the exact rename order and failure rollback sequence;
- when or whether the backup is deleted;
- whether uninstall removes the installed payload directory.

AppManager itself contains no matching package-directory rename/backup choreography. That operation, if used, remains inside the AMS boundary.

## Interruption windows and surviving state

The recovered ordering exposes several state-divergence windows. This table states only what the static evidence supports.

| Window | State that may already have changed | State not yet guaranteed | Static consequence |
| --- | --- | --- | --- |
| AMS installation succeeds before `finishInstall` | AMS-owned package/filesystem state | AppManager map finalization and persistent JavaApps list | Package/AMS state can be newer than AppManager persistence |
| `finishInstall` moves resources before list save | Some files under `<appId>/data/`; in-memory app state | Completion of every `mv`; persistent list write | Partial resource placement can be untracked because return codes are ignored and the vector is cleared |
| `saveJavaAppsList` between its separate read and write | Native map may have changed | Database value | No caller-side transaction or CAS protects the read/rebuild/write sequence |
| QDB statement execution | Journal and database may be in old/new transition | Power-loss durability | `journal_mode=truncate` is configured, but sync/flush guarantees are unknown |
| AMS uninstall succeeds before `finishUninstall` | AMS-owned package state may have changed | cleanup, native-map deletion, persistent list save | Persistent list can still name an application AMS considers removed |
| cleanup completes before queued map deletion | resource/RMS cleanup may have occurred | native map and database removal | Runtime/native state can remain stale |
| map deletion completes before queued list save | volatile native map no longer contains app | QDB JavaApps JSON | A restart can encounter a stale persistent entry; reconciliation is unknown |
| temp cleanup or resource move is interrupted | prefix of sequential `rm`/`mv` operations | remaining files and bookkeeping durability | No journal, rename group, or retry list is visible in AppManager |
| AMS installation-directory rename is interrupted | `prog`, staged `prog`, and `prog.bak` may be in transition | filesystem durability and cross-layer outcome | Normal rename/recovery choreography is proved, but power-loss persistence and AppManager/QDB/DRM reconciliation are not |
| QDB reports key-value corruption | recovery log | preservation of `key_value` database | `qdb_recover.sh` deletes `key_value*` and resets |

The native application map, queued event names, controller flags, and resource vectors are process memory and do not themselves provide reboot persistence. The QDB value and files under MMC/ETFS are intended persistent state, but exact filesystem flush timing is not present in the static evidence.

## Direct answers

### What is the persistent AppManager application registry?

**[CONFIRMED]** AppManager persists the native Java-app map as one JSON array under PersistentKeyValue key `AppManager_JavaApps`. The provider's default database store routes it to the QDB key/value database configured as `/usr/var/qdb/key_value`, table `keyvalueTbl`.

### Is install/upgrade/uninstall atomic across AMS, filesystem, native map, and registry?

**[CONFIRMED]** No. The visible phases are separate callbacks, event-queue entries, shell commands, native-map mutations, IPC calls, and one-value SQL statements. No cross-layer transaction or recovery journal connects them.

### Does uninstall remove the application-owned payload directory?

**[UNKNOWN]** AppManager delegates uninstall to AMS and does not directly remove `/fs/mmc1/xletsdir/xlets/<appId>`. The separate `/fs/mmc1/apps/%s` deletion service is not statically connected. The AMS AOT method performing uninstall has not yet been recovered sufficiently to prove payload deletion or retention.

### Is there a prior-version backup?

**[CONFIRMED]** `Installer.upgrade` invokes `recoverProgIfNeeded`, stages the new package, moves current `prog` to `prog.bak`, promotes staged `prog`, and removes backup/staging after success. `recoverProgIfNeeded` restores a backup only when `prog` is absent. **[UNKNOWN]** remains filesystem durability, boot-time reachability after interruption, and coordination with AppManager resources, QDB, RMS, and DRM.

## Highest-value unresolved questions

1. What is the exact bytecode-level rename order in `Installer.install`, `Installer.recoverProgIfNeeded`, and `Installer.upgrade`, including backup creation, restoration, commit, and deletion?
2. What is the exact successful uninstall filesystem sequence, and does it remove, retain, or rename `/fs/mmc1/xletsdir/xlets/<appId>`?
3. Does AMS rebuild or reconcile AppManager's `AppManager_JavaApps` list after an interrupted install/uninstall or deleted QDB database?
4. What QDB synchronous/flush policy is active for `/usr/var/qdb/key_value`, and what old/new result is guaranteed under sudden power loss?
5. Can concurrent AppManager lifecycle events produce a lost full-list update despite the event dispatcher, or are they serialized by an independently proved single queue?
6. What exactly occupies `/fs/mmc1/xletsdir/tmp/` during install and upgrade, and which files survive each failure status?
7. Does the AMS `prog.bak` path cover only the program payload, and how are properties, DRM/index data, RMS, and post-install resources coordinated with it?

Until those questions are closed, rollback design must use the stock per-app lifecycle boundary, stable power, before/after inventory checks, and a deliberately inert non-autostart test package. It must not depend on copying directories behind AMS or assuming that a successful IPC response makes every persistent layer mutually consistent.
