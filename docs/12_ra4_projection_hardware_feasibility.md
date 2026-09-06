# 12 - RA4 projection hardware and codec feasibility

Updated 2026-09-06. This report separates three questions that must not be
collapsed: what the OMAP3730 silicon contains, what the recovered RA4 actually
configures, and what a legitimate projection engine can call. It is static and
read-only. It authorizes no radio write, package installation, firmware change,
credential use, or protocol workaround.

## Decision

**SILICON/DISPLAY PLAUSIBILITY: HIGH.** The exact RA4 configuration targets a
640x480 display and names OMAP3730/SGX530 graphics components. TI identifies the
OMAP3730 as Cortex-A8 plus IVA2.2 plus SGX530. An adjacent OMAP3530/IVA2.2
reference codec demonstrates 640x480 H.264 Baseline decoding at 30 frames per
second.

**INSTALLED VIDEO-DECODE PATH: UNKNOWN.** The tracked evidence does not identify
a stock H.264 decoder, DSP codec server, Codec Engine shim, OpenMAX component, or
supported client ABI. QNX's historical public OMAP Codec Engine example is useful
proof that a QNX 6.4 integration family existed, but its prebuilt MME component
is explicitly an audio decoder. It is not evidence that RA4 contains video
decoding support.

**RESIDENT ENGINE DECISION: OPEN.** Hardware capability alone neither approves
the QNX Smartphone Connectivity candidate nor forces external compute. The
resident engine remains unclassified until the recovered filesystems are
censused, an authorized engine manifest is sized, and RAM/CPU/latency are measured
on spare hardware.

## Evidence ladder

| Layer | Evidence | Result |
| --- | --- | --- |
| Exact recovered RA4 | `graphics.conf` SHA-256 `984bfe3e698cf33f565c7698d98ea6aff2a59d568799e8a8d5a0ba0986204e93` names the OMAP3730 graphics directory, SGX530 drivers, 640x480@60, `video_hmi`, and CMC mtouch | **CONFIRMED** configured display/touch infrastructure; not decoder access or achieved frame rate |
| Exact recovered RA4 | ROV `main.xml` SHA-256 `d020a5b5049e87907b3deddff8c17cbf56fac24fa5dd235d4392a39e9ba23806` requests AIR GPU render mode; `qnxair.conf` has a commented `enable_gles` | **CONFIRMED** request/config text; actual GPU acceleration remains UNKNOWN |
| Exact SoC family | TI's AM/DM37x comparison table identifies OMAP3730 as Cortex-A8 + IVA2.2 + SGX530 | **CONFIRMED** silicon blocks, not installed QNX drivers/codecs |
| Adjacent TI reference | TI's OMAP3530 H.264 Baseline decoder data sheet reports VGA 640x480 YUV420 at 5 Mbit/s and 30 fps using average 262 and peak 303 MCPS in its stated 350 MHz DSP test configuration | **CONFIRMED for that OMAP3530 reference only**; **HIGH** evidence that VGA decode is plausible on the related IVA2.2 class, not an RA4 benchmark |
| Historical QNX integration | QNX's OMAP Codec Engine 1.2.0 technote targets QNX 6.4 on OMAP3530, with DSPLink, CMEM, `libcodecengine.so`, a DSP image and an io-media filter | **CONFIRMED** that an era-appropriate QNX/DSP integration pattern existed |
| Historical QNX prebuilt scope | The same technote names accelerated AAC, MP3 and WMA and supplies `ce_audio_decoder`; bounded text search has no H.264 or video match | **CONFIRMED NEGATIVE for that document/prebuilt description only**; it does not rule out other licensed QNX packages |
| Current tracked project text | A full scan of 85 tracked text/source blobs at commit `0fbf66d` for `libOMX`, `OMX_`, `OpenMAX`, `libavcodec`, GStreamer, H.264, MPEG-4, IVA2.2, DSPBridge, Ducati, PVR/GLES and Screen-window-buffer terms found only the prior analysis-plan H.264 search instruction | **CONFIRMED NEGATIVE for tracked text only**; ignored recovered firmware was not available to this API scan |

Primary sources:

- TI AM/DM37x versus OMAP35x comparison, including the OMAP3730 block set:
  https://www.ti.com/lit/pdf/sprab80
- TI OMAP3530 H.264 Baseline decoder performance data:
  https://software-dl.ti.com/dsps/dsps_public_sw/codecs/OMAP35xx/OMAP35xx_latest/H264_Decoder_OMAP3530_Datasheet_2_01_007.pdf
- TI OMAP35x codec catalog, which labels the reference decoder
  H.264 BP Level 3.0 and WVGA/D1 at 30 fps:
  https://www.ti.com/tool/OMAP35XCODECS
- QNX Aviage Multimedia Interface for TI OMAP Codec Engine 1.2.0:
  https://fusion.qnx.com/3/19913/mme_omap.pdf
- QNX Screen configuration model, where `graphics.conf` selects
  platform-specific GPU/display libraries:
  https://qnx.com/developers/docs/7.0.0/com.qnx.doc.screen/topic/manual/cscreen_config_intro.html

The TI codec download sizes are host delivery-package sizes, not target installed
bytes. They must not be entered into the 15 MB RA4 installed budget.

## What the QNX reference warns about

The QNX technote's example startup reserves `0x02600000` bytes for the codec
engine and `0x00200000` bytes for DSPLink: 38 MiB plus 2 MiB, or 40 MiB total.
It also requires a DSP image, QNX-ported DSPLink, CMEM, Codec Engine libraries,
the relevant codec/server, a QNX toolchain, and TI tools/licenses.

That 40 MiB is a reference **RAM reservation**, not storage consumption, and it
belongs to an OMAP3530 audio-oriented demonstration rather than RA4 or a
projection engine. It is not a product estimate. It is direct evidence that
"reuse the DSP" is not a zero-cost assumption and that reserved-memory/BSP
configuration must be measured before accepting a resident decoder.

At 640x480, one tightly packed YUV420 frame is 460,800 bytes; one RGBA frame is
1,228,800 bytes. These are arithmetic lower bounds only. Reference frames,
stride/alignment, encoded input, compositor queues, textures, IPC buffers and
runtime heap are additional and profile/implementation dependent.

## New bounded corpus probe

`analysis_tools/qnx_media_runtime_probe.py` performs the missing recovered-tree
census without executing vendor code. It:

- walks one or more supplied recovered roots without following symlinks;
- scans bounded files in chunks for a controlled media/graphics marker set;
- handles markers split across chunks without double counting;
- emits relative paths, file sizes, SHA-256, marker counts and bounded offsets;
- emits no file contents or arbitrary surrounding strings;
- reports every file skipped by the configured size ceiling.

Suggested read-only use after local execution recovers:

```text
python -m analysis_tools.qnx_media_runtime_probe \
  analysis_ra4_18.45.01/work/hidden_hbc_ifs \
  analysis_ra4_18.45.01/work/primary_iso \
  --pretty > qnx_media_runtime_evidence.json
```

The JSON output may contain vendor filenames and local evidence metadata. Review
and sanitize it before deciding whether any derived result belongs in Git. Never
commit recovered libraries, DSP images, codecs, firmware, or payloads.

The committed synthetic tests cover cross-chunk detection, deduplication, offset
caps, hashes, relative paths, non-disclosure of unrelated content, explicit
oversize skips, and multi-root totals. They are not reported as executed because
the local command service currently cannot start a trivial process.

## Legacy QNX 6.6 CarPlay transport boundary

Official QNX 6.6-era Device Publishers documentation explicitly supports Apple
CarPlay USB role swap through `usblauncher`,
`RoleSwap_DigitaliPodOut`, and `io-usb-dcd`. This improves platform-era
plausibility but does not establish video decode: the page describes transport
and directs integrators to QNX support for automotive iOS drivers. It supplies
no receiver binary, H.264 decoder identity, RA4 controller/BSP claim, RAM usage,
or installed size. TI's OMAP36xx/37xx TRM confirms the OTG block can operate in
host/peripheral modes, but QNX's public OMAP3730 BSP feature table lists OTG only
as host. The UCI cable is now mapped at Radio C2 D2784B to one USB power/D-/D+/
ground path. Because the combined SD-reader/user-USB module shares that one
upstream pair, active hub/controller or mux logic is required; its reversibility,
VBUS behavior, the BE2800 internal route and custom RA4 DCD remain unknown.

The recovered-tree census therefore includes exact legacy Apple transport
markers alongside Codec Engine/OpenMAX/GStreamer/DSP and projection-service
markers. A transport hit cannot close the decoder gate; a decoder hit cannot
close authentication or UI/audio integration.

See [QNX 6.6 CarPlay transport reference](17_qnx6_carplay_transport_reference.md)
and [OMAP3730 USB role feasibility](18_omap3730_usb_role_feasibility.md).

## Acceptance path

A positive filename/string result is only a candidate. For each candidate:

1. record source-image provenance, relative path, byte size and SHA-256;
2. classify ELF architecture and imports without execution;
3. identify boot/startup evidence for DSPLink, CMEM, codec-server and reserved
   memory;
4. distinguish audio-only filters from H.264 video decode;
5. identify a supported client API/ABI and its owner-death/cleanup behavior;
6. determine whether licensing permits reuse by an authorized new application;
7. measure installed incremental bytes, reserved/steady/peak RAM, CPU, frame
   latency, buffer count and stock camera/HMI behavior on a spare RA4.

A negative complete census would prove absence only for the recovered
18.45.01 trees and controlled markers. Stripped binaries, alternate names and
dynamic construction require import/call-graph follow-up. A positive codec
library still does not prove spare capacity, client permission, or compatibility
with an authorized projection engine.

## Resource result

This investigation and probe install 0 bytes on the radio and create 0 radio
writable or staging bytes. Product limits remain 15 MB installed, 4 MB normal
writable growth, 8 MB additional staging/rollback, and at least 45 MB protected
stock reserve. Hardware acceleration receives no zero-byte credit until an
installed, compatible and permitted stock interface is proved.

The best next technical target is the hash-identified recovered-filesystem
media-runtime census, followed by import/startup correlation for every candidate.
In parallel on the legitimate-provider path, obtain component-level target
sizes and RAM requirements for the QNX Smartphone Connectivity build. Only a
failed compatibility or measured resource gate makes the projection engine
`EXTERNAL_COMPUTE_REQUIRED`.
