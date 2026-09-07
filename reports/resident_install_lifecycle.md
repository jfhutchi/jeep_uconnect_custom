# RA4 Resident Install and Lifecycle Contract

## Result

The legitimate runtime owner is AppManager/AMS, not direct filesystem or QDB
editing. Two stock ingress paths converge on authenticated package inspection
and AMS install/upgrade, followed by separate native catalog persistence. The
protocol shape is proved; a newly authored accepted package and safe target
transaction are not.

## Ingress paths

### Authorized application media

```text
authenticated SWDL media and installer ISO
  -> external app installer selected by signed manifest
  -> <ISO_PATH>/usr/share/APPS/<directory>/<package>.jar
  -> copy to /fs/mmc0/xlets/temp/<package>.jar
  -> AMS getPackageInfo(file URI, auth=false) metadata preview
  -> install if app absent, upgrade if present
  -> delete staged copy after the returned operation status
```

This is **PROVED** from the media loader and Lua bytecode except for the missing
external manifest and missing live package sample. `auth=false` is only the
metadata-preview argument; secure AMS and the later operation remain in force.

### Catalog/Application Manager

```text
catalog response (schema partly recovered)
  -> download to /fs/mmc1/download/<huFileName>
  -> CRC32 transport-integrity check
  -> native AppManager installApp(appId, basename)
  -> authenticated AMS getPackageInfo(uri, auth=true)
  -> AMS adapter operation upgrade
```

CRC32 does not authenticate the application signer. Native catalog installation
uses AMS `upgrade` even for the catalog's fresh-install task. AMS `upgrade`
delegates to `install` when the target app directory is absent, so its upsert
behavior is **PROVED**.

## Installation completion

The native completion ordering is **PROVED**:

```text
authenticated package-info
  -> AMS install/upgrade response plus onInstalled signal coordination
  -> finishInstall
  -> update native application object
  -> move tracked post-install resources
  -> revoke write access
  -> conditional autostart decision
  -> emit appListUpdated
  -> queue whole AppManager_JavaApps JSON persistence
```

AMS stages under fixed `__newxlet__`, then creates a new app directory for
install or swaps only `<appId>/prog` for upgrade. Upgrade renames current `prog`
to `prog.bak`, promotes staged `prog`, and removes backup/staging after success;
`data` persists. `recoverProgIfNeeded` restores `prog.bak` only if `prog` is
missing. Exact power-loss durability and coordination with AppManager remain
**UNKNOWN**. AppManager's filesystem/resource operations and whole-list QDB save
are not one transaction with AMS package mutation.

## Registration and manual launch

`AppManager_JavaApps` is stored through PersistentKeyValue in QDB
`/usr/var/qdb/key_value` as a complete JSON array. Entries visibly contain
`appId`, `appName`, and `medName`. This downstream catalog must not be edited to
manufacture installation.

An ordinary non-autostart install can finish stopped. The proved user-facing
start path is:

```text
generic Apps list selection
  -> HMI startXlet(selected appId)
  -> native AppManager startApp request
  -> findAndStartApp(appId, DRM check enabled)
  -> AMS start
  -> Xlet lifecycle init/start and foreground handling
```

Whether a newly authorized identity appears in `getAppList`, owns the expected
foreground surface, and returns cleanly is a separate bench runtime gate.

## Uninstall

The stock success path is **PROVED** through the following boundary:

```text
AppManager uninstallApp(appId)
  -> stop/wait if necessary
  -> obtain write access
  -> AMS uninstall response plus completion signal
  -> finishUninstall
  -> remove tracked Xlet resources
  -> remove per-app RMS directory and shared RMS record
  -> delete native-map entry
  -> emit appListUpdated
  -> queue whole JavaApps list save
```

Still **UNKNOWN**: whether AMS deletes, retains, or renames the installed payload
directory; interruption reconciliation; exhaustive application-owned paths;
and reliable previous-version restoration. These keep the rollback/recovery
gate closed even after a legitimate package is obtained.

## Legitimate shortest path

The shortest technically supported future path is not direct copying. It is an
authorized issuer producing the now-schema-defined but still unauthorized signed JAR and
identity/DRM/policy records, followed by the stock AppManager/AMS install path on
a spare bench RA4, with a documented stock uninstall route and recovery plan.
Service certificates, engineering gestures, direct Xlet/QDB edits, insecure AMS,
DRM disabling, or stock identity reuse do not satisfy this contract.
