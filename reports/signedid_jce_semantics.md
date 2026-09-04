# RA4 `SignedId` JCE and RSA Semantics

## Scope and safety boundary

This report closes the provider-default transformation question left by the `xlet.developerToken` trace. It uses only static reads of the owner-supplied RA4 18.45.01 AMS image and original metadata decoding. No target executable was run, no private key or token plaintext was recovered, and no firmware, JAR, certificate, or persistent vehicle state was modified.

Canonical artifact:

- `analysis_ra4_18.45.01/work/primary_iso/usr/share/MMC_IFS_EXTENSION/bin/AMS`
- Size: 11,956,352 bytes
- SHA-256: `96683b789ecf06a8575915d0b446b532e1f4ee87feb31d925cb7ba3d7d324d27`
- Jamaica object mapping: virtual address = file offset + `0x100000`

The final result is RA4-confirmed:

```text
Cipher.getInstance("RSA")
  -> installed provider service Cipher.RSA
  -> com.sun.crypto.provider.RSACipher
  -> algorithm-only Transform(mode=null,padding=null)
  -> no engineSetMode/engineSetPadding call
  -> RSACipher constructor default PKCS1Padding

Cipher.init(DECRYPT_MODE, RSA public key)
  -> RSACipher internal MODE_VERIFY
  -> PKCS#1 v1.5 block type 1
  -> public RSA operation
  -> RSAPadding.unpad(...)
  -> exact plaintext String equality with developerId
```

`RSA/ECB/PKCS1Padding` is therefore the exact conventional transformation label for the RSA candidate used by `SignedId`; `ECB` is the provider's only accepted nominal RSA mode and does not describe a block-cipher chaining operation.

## ROM class ownership

The little-endian class-pointer table is file `[0xB1BC48,0xB20424)`. Pool-backed self-name markers and adjacent pointers give these exact class objects:

| Class | Pointer slot | File bounds | Size | Bounded SHA-256 |
| --- | ---: | --- | ---: | --- |
| `com/sun/crypto/provider/RSACipher` | 587 | `[0x5E4D78,0x5E5598)` | 2,080 | `bbb6e22998315061ca4b69d5db2c569a23a788839514080dce4212e15324da13` |
| `com/sun/crypto/provider/SunJCE` | 592 | `[0x5E5BB0,0x5E5CF0)` | 320 | `d3d7ce87ce98feffbbee58f3758cac1b838e4766b60edd2b727b3a2aa1f028db` |
| `com/sun/crypto/provider/SunJCE$1` | 593 | `[0x5E5CF0,0x5E6668)` | 2,424 | `e217d1fa6e1ac5f23b8c239f2d07fe2bcc60253deb509dad0c5747ad1583e83c` |
| `javax/crypto/Cipher` | 2,029 | `[0x6E6998,0x6E80E8)` | 5,968 | `a8dc47f3de5942eaa62eed7bf0e459df4ad77903561cee670cfc79fa694eca31` |
| `javax/crypto/Cipher$Transform` | 2,030 | `[0x6E80E8,0x6E8320)` | 568 | `c5d038551229b26a868419afe0416e5a74ddb6ff8ab2f88b92cbff1401640f5c` |
| `sun/security/rsa/RSAPadding` | 3,355 | `[0x79C8E8,0x79CFB0)` | 1,736 | `a775bbafc9f2faf4ba18e1ce16c9a095997407e0c416c389ca02f7ddb72a07c4` |

The corresponding self-name markers are at file `0x5E4EFA`, `0x5E5C07`, `0x5E5F7B`, `0x6E6AAC`, `0x6E8170`, and `0x79C8E9`. Their one-based pool IDs resolve through the complete name pool `[0x9C2071,0xAB8ECC]`.

## Installed provider and RSA service

The embedded Java security resource lists the provider order directly:

| Provider line | File offset |
| --- | ---: |
| `security.provider.1=sun.security.provider.Sun` | `0x899E43` |
| `security.provider.2=sun.security.rsa.SunRsaSign` | `0x899E71` |
| `security.provider.3=com.sun.net.ssl.internal.ssl.Provider` | `0x899EA1` |
| `security.provider.4=com.sun.crypto.provider.SunJCE` | `0x899EDB` |
| providers 5 through 8 | `0x899F0E`, `0x899F40`, `0x899F73`, `0x899FAF` |

The complete provider-list block `[0x899E43,0x899FE5)` is 418 bytes with SHA-256 `18e2f729eb57da4f2ed0abe2f6a4957ee845a21c6d53060c8a89e535f3893e9b`.

The service registration is executable metadata, not a nearby-string inference. `SunJCE$1` constant-pool entries and its `run()` bytecode bind:

| CP entry | CP header | Decoded value |
| ---: | ---: | --- |
| 2 | `0x5E5CF7` | `Cipher.RSA` |
| 3 | `0x5E5CFA` | `com.sun.crypto.provider.RSACipher` |
| 5 | `0x5E5D02` | `Cipher.RSA SupportedModes` |
| 6 | `0x5E5D05` | `ECB` |
| 7 | `0x5E5D08` | `Cipher.RSA SupportedPaddings` |
| 8 | `0x5E5D0B` | `NOPADDING|PKCS1PADDING|OAEPWITHMD5ANDMGF1PADDING|OAEPWITHSHA1ANDMGF1PADDING|OAEPWITHSHA-1ANDMGF1PADDING|OAEPWITHSHA-256ANDMGF1PADDING|OAEPWITHSHA-384ANDMGF1PADDING|OAEPWITHSHA-512ANDMGF1PADDING` |

The first calls in `SunJCE$1.run`, beginning at file `0x5E5FB3`, load CP pairs 2/3, 5/6, and 7/8 and call the enclosing provider's `put` method. The bounded record `[0x5E5FB3,0x5E5FE2)` is 47 bytes with SHA-256 `3a041bbeb518834fc60ff921b106c63548f74035caf45a08fa136c0828fabc2e`.

The compact literal reference for `Cipher.RSA` occurs in executable class metadata only at `0x5E5CF7`; the other raw byte-pattern occurrence is inside the decoded string-pool storage itself. This supports SunJCE as the registered RSA Cipher implementation in this image. The earlier providers are still preferred for services they implement, but the recovered RSA `Cipher` service is SunJCE's `RSACipher`.

## Algorithm-only `Cipher` selection

`SignedId.decrypt(PublicKey)` supplies only `key.getAlgorithm()` to `Cipher.getInstance`. For the promoted Chrysler or Xlet Developer RSA certificate this string is `RSA`; no slash, mode, padding, or provider is supplied.

`Cipher.tokenizeTransformation(String)`, selector `0x44FC` at file `0x6E6F0E`, creates a three-element array and leaves absent mode and padding elements null. `Cipher.getTransforms(String)`, selector `0x44FD` at `0x6E6FD5`, reads those elements and, when both are null, constructs exactly one `Cipher$Transform` with the algorithm and null mode/padding fields. Its complete bounded record `[0x6E6FD0,0x6E70C8)` is 248 bytes, SHA-256 `04cbe5d9754a40b96b8dedd867b2f284a4fcfc8edb1f5c3a258c3695347feb48`.

`Cipher.getInstance(String)`, selector `0x451F` at `0x6E7115`, calls `getTransforms`, obtains matching provider services, checks service/provider eligibility and supported mode/padding, and constructs or defers the `CipherSpi`. The bounded code slice `[0x6E7110,0x6E7218)` is 264 bytes, SHA-256 `3168146f9ba6ea8216d855c944b496e683a3e31c6d481607f9e25487683cde7d`.

Most importantly, `Cipher$Transform.setModePadding(CipherSpi)`, selector `0x4534` at `0x6E81F4`, tests each field for null before invoking `CipherSpi.engineSetMode` or `engineSetPadding`. The body at `0x6E81FC..0x6E821C` therefore invokes neither setter for the algorithm-only `RSA` transform. The bounded method record `[0x6E81EE,0x6E821D)` is 47 bytes, SHA-256 `a18fe7210a368c64293382dd748c21fb35f9ea38ff93ad4596b24814f3d75220`.

## `RSACipher` defaults

The `RSACipher` constant pool resolves:

| CP entry | CP header | Meaning |
| ---: | ---: | --- |
| 2 | `0x5E4D7E` | literal `SHA-1` |
| 3 | `0x5E4D81` | self field local member `0x10`, `oaepHashAlgorithm` |
| 6 | `0x5E4D90` | literal `PKCS1Padding` |
| 7 | `0x5E4D93` | self field local member `0x09`, `paddingType` |
| 8 | `0x5E4D98` | literal `ECB` |
| 17 | `0x5E4DBD` | literal `NoPadding` |

The complete constructor record `[0x5E4F6F,0x5E4F90)` is 33 bytes, SHA-256 `956ac714d1adf1a4d7e8924b6a166aeed5006b75f06d9509098890c0f8883c3e`; its bytecode is `[0x5E4F76,0x5E4F8E)` (24 bytes, SHA-256 `3b4f32df0cd63565b1c1332a3ba4ebfd3117e6ecc24372c3c8691cc1b03c7269`). It calls the superclass constructor, stores `SHA-1` in `oaepHashAlgorithm`, performs the SunJCE integrity check, stores `PKCS1Padding` in `paddingType`, and returns. The integrity check does not replace either default.

`engineSetMode(String)`, selector `0x0E07` at `0x5E4F91`, accepts `ECB` case-insensitively and throws for anything else. `engineSetPadding(String)`, selector `0x0E08` at `0x5E4FC2`, recognizes `NoPadding`, `PKCS1Padding`, and the listed OAEP spellings. Because `Cipher$Transform` skips both setters for bare `RSA`, the constructor's `PKCS1Padding` value remains active. The OAEP hash default is present in the implementation but is not used by this token path.

## Public-key decrypt semantics

The private `RSACipher.init(int,Key,SecureRandom,AlgorithmParameterSpec)` selector is `0x0FA3` (global selector record `0xAD9BB8`, class marker `0x5E5127`). Its bounded record `[0x5E5123,0x5E5265)` is 322 bytes, SHA-256 `5aaaf03783fbadfda339e2ebe386ddfc4d8384adbdb20ff1e8e652ebf6a45812`.

The bytecode proves the following decisions:

1. The operation-mode switch at `0x5E512F` treats Java modes 1/3 as the forward/private-input branch and modes 2/4 as the reverse branch; any other value throws.
2. After `RSAKeyFactory.toRSAKey`, the public-key branch at `0x5E5178..0x5E519F` maps reverse mode to numeric internal mode 4.
3. Class metadata at `0x5E4F02..0x5E4F13` binds internal values 1, 2, 3, and 4 to `MODE_ENCRYPT`, `MODE_DECRYPT`, `MODE_SIGN`, and `MODE_VERIFY`; numeric 4 is therefore `MODE_VERIFY`.
4. The `PKCS1Padding` branch at `0x5E5200..0x5E5254` selects padding type 1 whenever the internal mode is greater than 2. Global `RSAPadding` selector records bind `PAD_BLOCKTYPE_1` at `0xB03B10` and `PAD_BLOCKTYPE_2` at `0xB03B18`.
5. The `RSACipher` final-operation switch in bounded slice `[0x5E52AC,0x5E53B0)` (260 bytes, SHA-256 `7b0dba77fc7a6e09a41c3a19a022af97859c96a14104c41c7c682d4ab9554324`) sends internal mode 4 through the RSA public-key primitive and the `RSAPadding.unpad` branch. Global selectors identify `pad([B)[B` at `0xB03AC8`, `unpad([B)[B` at `0xB03AE0`, and their ranged overloads at `0xB03B50`/`0xB03B58`.
6. `RSAPadding.unpad(byte[])`, marker `0x79CC45`, dispatches types 1 and 2 to `unpadV15` in body `0x79CC4E..0x79CCA8`. The complementary `padV15` body `0x79CCBA..0x79CD5D` visibly constructs type 1 as `00 || 01 || FF... || 00 || payload`, independently confirming PKCS#1 v1.5 type-1 layout. `unpadV15` itself is AOT/native form, so its precise rejection checks and timing are not recovered.

Consequently, `Cipher.init(2, publicKey)` in `SignedId` is not OAEP and does not verify a Java `Signature` object or a digest container. It performs the provider's RSA public-key decrypt/verify operation and removes a PKCS#1 v1.5 type-1 envelope before `SignedId` constructs a `String` and compares it exactly with `developerId`.

## Trust-model consequence

The RSA primary signer promoted by production is Chrysler UConnect Application CA; development substitutes Xlet Developer. The shared aicas candidate is DSA. A DSA candidate cannot instantiate the recovered `Cipher.RSA` service and simply fails that `SignedId.verify(PublicKey)` attempt through the already-confirmed exception-to-false path; the array overload continues to other keys.

The consumer-side credential format is now bounded precisely. A successful token must have been produced by the complementary private-key authority for the matching promoted RSA identity and must recover to the exact live `developerId`. This is an issuer boundary, not an invitation to synthesize, replay, or guess credentials: the private keys and legitimate issuance service are absent from the corpus, and no safe design may substitute a copied stock token or weaken this verifier.

## Remaining unknowns

- The legitimate Chrysler/Xlet Developer credential-issuance workflow and authority remain unknown.
- The recovered update corpus still supplies no working reflected `Device.getDeveloperId` implementation; a live-unit overlay remains only a theoretical source.
- A corpus census found no recovered JAR/ZIP entry naming `insertProviderAt`, `addProvider`, `removeProvider`, or `security.provider.`, and no recovered boot/config provider override. This supports the stock provider result but cannot exclude mutable live state absent from the update.
- `new String(byte[])` still uses the platform default charset. No explicit charset appears in `SignedId`; exact live default-charset configuration remains to be proved. An ASCII-like identifier is plausible but is not yet evidence.
- Certificate-array ordering and the later signer/principal/policy assignment remain unresolved.
- This result does not make the anti-theft PIN, IOC state 4, service-certificate gate, or `/fs/etfs/AMS_DEVELOPMENT` part of token generation. Those domains remain separately authenticated and separately traced.

## Reproduction notes

The names above reproduce with `analysis_tools/jamaica_rom_strings.py` using pool start `0x9C2071`, terminator mode, literal table `0xAB8ED0` with 25,587 records, member table `0xAD1EA0` with 28,142 records, and the little-endian class-pointer table at `0xB1BC48`. All parsing was bounded to the stock AMS file; no embedded code was executed.
