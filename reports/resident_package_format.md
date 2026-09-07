# RA4 Resident Package Format

## Result

RA4 18.45.01 exposes two stage-specific representations, and AMS now proves the
exact transformation between them.

1. **PROVED - live installer input:** both recovered live ingress paths hand one
   direct local payload JAR filename or `file:` URI to AppManager/AMS. The
   recovered production form is conventionally signed. AMS opens that JAR
   directly, authenticates it, and splits its members; there is no nested
   executable JAR or nested `key.jar`.
2. **PROVED - factory/post-install form:** KIM content and AMS path construction
   establish an external runtime descriptor, executable JAR, fixed detached
   `key.jar`, and `magic.txt` beneath an application-ID directory. This is an
   installed-layout contract, not evidence that the same directory tree is an
   accepted live input.

The current Hello `xlet.properties` is therefore a logical descriptor and the
generated research directory is only an incomplete installed-layout model. A
raw Hello JAR plus that external file is not a proved install package.

## Incoming and outer containers

| Layer | Status | Recovered contract |
| --- | --- | --- |
| Removable-media update | **PROVED** | Media detection expects `/fs/usb0/swdl.upd`, mounts it at `/fs/swdl`, authenticates present nested `installer.iso`, `primary.iso`, and `secondary.iso`, requires/mounts `installer.iso`, then loads its manifest. |
| External app-media dispatcher | **PROVED / sample UNKNOWN** | An authenticated installer manifest may name `manifest.external.start_script`; `us-app-install.sh` invokes the app installer with `ISO_PATH` and `USB_PATH`. Stock 18.45.01's full-update manifest has no such external member, so the selecting manifest is absent. |
| App-media application object | **PROVED boundary and schema** | `us-app-install.lua` walks `<ISO_PATH>/usr/share/APPS/<directory>/*.jar`, copies one JAR to `/fs/mmc0/xlets/temp/<filename>`, previews it with AMS `getPackageInfo`, and submits its file URI to `install` or `upgrade`; AMS treats that file itself as the direct payload archive. Recovered production inversions have conventional JAR signature members; exact signature-block requirements for an authorized developer-token-only path remain unknown. |
| Catalog application object | **PROVED boundary and schema** | KIM3 downloads one server-named JAR to `/fs/mmc1/download`, verifies transport CRC32, and passes the basename to native AppManager. Native AppManager resolves it in the fixed download directory and performs authenticated AMS package-info preflight over the same direct JAR. Recovered production inversions are conventionally JAR-signed; an original live sample and token-only acceptance contract are absent. |
| Factory KIM population | **PROVED** | The software-update `xlets` installer copies a selected KIM tree into `/fs/mmc1/xletsdir/xlets`; KIM copy manifests record MD5, length, and destination. This is factory provisioning, not the live single-JAR schema. |

The `swdl.upd`/nested-ISO signature is an outer software-update control. It does
not replace application-byte authentication, and possession of the public SWDL
verification key cannot authorize a new installer ISO.

## Proved installed layout

For each observed KIM application:

```text
<appId>/
`-- prog/
    |-- xlet.properties               installed/runtime descriptor
    `-- jars/
        |-- <installed executable>.jar
        |-- key.jar                   fixed detached signature envelope
        `-- magic.txt                 six ASCII bytes: HB_CMC
```

AMS constructs the runtime paths as:

```text
/fs/mmc1/xletsdir/xlets/<appId>/prog/xlet.properties
/fs/mmc1/xletsdir/xlets/<appId>/prog/jars/<xlet.jarFile>
/fs/mmc1/xletsdir/xlets/<appId>/prog/jars/key.jar
```

`key.jar` is not descriptor-selectable. Every one of the 135 recovered KIM
application instances has an external descriptor, descriptor-selected
executable JAR, and fixed companion `key.jar`. Every `key.jar` contains standard
ZIP/JAR members `META-INF/MANIFEST.MF`, at least one `.SF`, a paired `.RSA`, and
an embedded signed `xlet.properties`; none contains application classes.

**PROVED for all 135 recovered application instances:** the executable JAR
contains root `xlet.properties`, byte-identical to the signed copy in `key.jar`;
the installed external copy is the normalized third form. Every payload/key
pair is consistent with the recovered AMS split. The deterministic census has
135 consistent, zero inconsistent, zero invalid/unreadable layouts, and 65
distinct member content sets (`reports/resident_incoming_transform_census.json`,
SHA-256 `03159b95b64606bb92f0941413a884e59653584c3c1c5c6d4e347da64687255e`).

The 245 observed `magic.txt` instances are byte-identical (`HB_CMC`, 6 bytes,
SHA-256 `0ffe9823746d76b9fb74480676a68d052b3a11634f2dfe67bd9fe9c8f3cd1f80`).
Their use as a build/copy sentinel is **INFERRED**. Use as an AMS `Installer`
authentication input is **DISPROVED**: `Installer` creates neither the member
nor the file and uses the signer/token verification paths instead. Sentinel or
gating semantics in factory-copy, download, or pre-Installer components remain
**UNKNOWN**.

## Representative stock samples

| Sample | Installed descriptor | Executable JAR | Detached envelope | Structural result |
| --- | --- | --- | --- | --- |
| KIM1 Slacker, app ID `05096915-cc7e-4881-b53e-278f6d799862` | 1,042 bytes; SHA-256 `ea6550eeb9b1774d8ef356ae2165da7cd7bd20a775380107e9fae7f71fa5a53a` | 925,156 bytes; SHA-256 `329098c01cd0cbef808ca06778e57411be979108dfb35965ba2992c6fd5c8a47` | 52,183 bytes; SHA-256 `91a031d22e62e129177470e64533df772f1faad57a532cd4caddcb45518d1aa0` | 513/513 non-directory payload names covered; 1,026 digest records checked; zero mismatch; manifest digest matches. |
| KIM3 Application Manager, app ID `c1d77320-6335-48b2-aa22-21912f657311` | 587 bytes; SHA-256 `cf1ad2e4326821d334dd591a48d29ac30d886d9730844865655749278f8a53ff` | 836,379 bytes; SHA-256 `bcc4b7de1c7aad3c683c2831ef7f9d2b79e557d2c8bf1a2c6d2b7c252bc187d9` | 39,080 bytes; SHA-256 `13a2d3c861e6b02f61b1c86e5770b8766e64489604fc66e06b4daed7b4852202` | 580/580 payload names covered; 580 digest records checked; zero mismatch; manifest digest matches. |
| KIM1 Vehicle User Guide, app ID `079aa169-df8f-48b4-b331-4ed51dbf6b12` | 1,638 bytes; SHA-256 `7319c16b876610a6c9b2fbeb40164b791a8ae1c5ec839ae38b2a9f3fb13ac430` | 1,558,076 bytes; SHA-256 `382026942a6cde768c4c3762497523c3300a5c3fa101d8661b2b0dfacfe3b260` | 27,207 bytes; SHA-256 `faccde0e49150c883d2f7a247987ba48d20e90b5966bfdab9556ab70d8cf0e49` | Existing corpus verifier matched all 386 manifest digest records. |

All three executable JARs are ordinary ZIP/JAR containers. The first two were
rechecked with `resident_package_inspect.py`; their public signer certificate is
SHA-256 `9ebf781bd18ad8c1f33b5b4727a2bed922b6cd4fb9680250a30de68045f3f546`
(`Chrysler UConnect Application CA`). Certificate presence is public metadata,
not authority to issue a new signature.

## What remains unknown

- The authorized package-creation service or issuer-facing packaging tool and
  the original ZIP serialization of a legitimate live sample.
- Certificate-chain, time/revocation, signing-key promotion/cache, and
  signer-to-principal/policy internals.
- The issuer rules for app-ID allocation, policy/DRM grants, category, launcher
  masks, and installer type.
- Hidden native AppManager/DRM transaction state after AMS file promotion.

The complete schema and offset-level proof are in
`reports/resident_incoming_jar_schema.md`.

## Reproduction

```powershell
$py = 'analysis_work/post_reboot_20260906/venv/Scripts/python.exe'
& $py -m analysis_tools.resident_package_inspect analysis_ra4_18.45.01/work/secondary_iso/usr/share/XLETS/kim_packages/KIM1/xlets/05096915-cc7e-4881-b53e-278f6d799862 --pretty
& $py -m analysis_tools.resident_package_inspect analysis_ra4_18.45.01/work/secondary_iso/usr/share/XLETS/kim_packages/KIM3/xlets/c1d77320-6335-48b2-aa22-21912f657311 --pretty
Get-FileHash analysis_ra4_18.45.01/work/installer_iso/usr/share/scripts/app-install/us-app-install.lua -Algorithm SHA256
```

Primary evidence: `reports/application_install_pipeline.md`,
`reports/kona_application_authorization.md`, and
`reports/keyjar_runtime_association.md`.
