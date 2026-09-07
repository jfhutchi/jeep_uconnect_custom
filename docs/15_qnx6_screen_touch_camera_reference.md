# 15 - QNX 6.6 Screen, touch, and camera reference boundary

Updated 2026-09-06. This read-only official-reference comparison does not
authorize Screen calls, window creation, focus changes, input injection, camera
access, PPS writes, target launch, or radio installation.

## Result

**CONFIRMED REFERENCE:** QNX Screen composites windows from different rendering
technologies. Application, child, and embedded windows can form a managed
hierarchy. A window joining a parent group becomes positioned and visible
relative to that parent and inherits parent visibility and transparency. The
group owner receives child create/destroy events and has privileged access.

Input focus is not an application shortcut. The focus property is owned at
display/group scope, and display focus requires a privileged display-manager
context. Window sensitivity controls pointer/touch eligibility. Ownership,
visibility, focus, and sensitivity are separate gates.

The QNX CAR reference rear camera responds to vehicle state, fills the display
during reverse, and restores the previous display afterward. Its objects are not
the RA4 contract; the traced Harman camera flow is authoritative.

## Exact RA4 evidence

| Evidence | Status | Meaning |
| --- | --- | --- |
| hidden graphics.conf: OMAP3730/SGX530, 640x480@60, video_hmi, CMC mtouch/scaling | CONFIRMED configuration | display/input classes exist; new-app access unproved |
| QNX Screen/libscreen and window/buffer APIs in factory utilities | CONFIRMED | installed composition family; no projection contract |
| factory screen_get_event/mtouch calibration use | CONFIRMED | input exists; production ownership unproved |
| foreground admission 0x0025250E-0x002525D2; retry 0x002524C4-0x002524FD | CONFIRMED | stock HMI decides ordinary foreground |
| camera observation 0x002BA764-0x002BA89F | CONFIRMED | DisplayManager owns camera state/layer |
| camera takeover/return 0x002D4D6F-0x002D4EF8 | CONFIRMED | LayerManager shows camera and unwinds stack |
| HVAC popup 0x0026DA68-0x0026DAB9 | CONFIRMED | popup overlays without replacing branch |

Fixed addresses are evidence anchors, not stable APIs.

The later [RA4 display-owner trace](../reports/ra4_display_owner_reclaim.md)
connects the HMI DisplayManager destination to Lua LayerManager and then native
Screen visibility. An AMS service-owner callback hides `:AMS` and restores
default AMS/HMI layer orders. This is a service-wide reaction; per-Xlet hangs,
input/contact release and bounded recovery are still unproved. `:AMS` is an
observed policy/window key, not an established Screen group contract. The
captured native command table has no explicit focus/sensitivity entry, which
does not exclude management of those properties elsewhere.

## Required surface contract

~~~text
legitimate projection frame producer
          |
          v
one stock-registered projection surface
          |
          +-- visibility/z-order/focus controlled by stock manager
          +-- touch only while selected and unobscured
          +-- camera/critical layer preempts independently
          +-- comfort popup overlays without destroying surface
          |
          v
session remains active while surface is hidden
~~~

The surface cannot replace stock HMI, create an unparented always-on-top shell,
acquire privileged focus directly, inject touch into stock/camera windows,
infer permission from symbols, restart on visibility change, or intercept camera.

## Display and input state

The adapter separately observes session, stock foreground grant, visibility,
camera/critical takeover, overlay state, and input eligibility. Touch is eligible
only with a fresh active session, selected/visible proved target, no blocking
stock owner, and a valid coordinate/contact lifecycle.

A failed condition stops new touch. An in-progress contact must be cancelled or
ended according to the recovered stock contract; it cannot leak into the newly
visible camera or stock surface.

Return to Uconnect backgrounds the surface but preserves session. Return to
Projection requests stock foreground and reveals the existing surface. Stock
BacktoCar can call `callStartProjection(activePpId)` before checking session
state; its backend effect must be proved. Session/surface continuity remains
required. See the [checkpoint](../reports/ra4_post_reboot_checkpoint.md).

## Camera and overlay behavior

**CONFIRMED RA4:** front/side camera enters SCREEN_CAMERA and backs/removes it
when cleared; backup/cargo use camera popup layers. Preserve that difference.

**HIGH:** a stock-managed projection surface underneath camera should reappear
when the stock stack unwinds and the session remains active. Projection code
does not perform the camera transition.

A comfort popup remains stock-owned. Touch follows its actual input policy, not
visual transparency. The heated-seat/wheel trigger remains unproved.

## Unknowns

- exact RA4 Screen group owner and identifier;
- whether video_hmi is the correct projection class;
- window type and accepted registration path;
- pixel format, buffers, stride, usage and synchronization;
- z-order for projection, popup and camera variants;
- focus/sensitivity owner and legal client permissions;
- mtouch coordinates, scaling, contacts and preemption cancellation;
- owner-death cleanup and previous foreground restoration;
- PROJECTION_BACKTO_CAR consumer and return button path.

## Read-only census

The controlled probe adds screen_join_window_group, SCREEN_PROPERTY_FOCUS,
SCREEN_PROPERTY_SENSITIVITY, SCREEN_EVENT_MTOUCH_TOUCH, and video_hmi. A hit
requires architecture, imports, startup, graphics.conf, manager ownership, and
existing-client correlation. A string authorizes no Screen call.

## Resource effect

This report/probe are host-only: 0 RA4 installed bytes, writable growth, or
staging. Production uses stock Screen/mtouch, stores no frame cache on disk, and
bundles no graphics runtime. Live frame buffers count as RAM, not against the
77 MB storage observation, but need a RAM budget. Storage caps remain 15 MB
installed, 4 MB writable, 8 MB staging, 45 MB stock reserve, and 5 MB margin.

## Best next target

Run the census against recovered 18.45.01 roots; correlate video_hmi, Screen
group/focus and mtouch hits with imports/startup. Decisive evidence is the stock
window manager or existing video client showing group identity, class, buffers,
focus transfer and teardown. Also complete PROJECTION_BACKTO_CAR XREF.

## Official sources

- https://www.qnx.com/developers/docs/6.6.0_anm11_wf10/com.qnx.doc.screen/topic/manual/cscreen_about.html
- https://www.qnx.com/developers/docs/6.6.0_anm11_wf10/com.qnx.doc.screen/topic/manual/cscreen_compmanager.html
- https://www.qnx.com/developers/docs/6.6.0.update/com.qnx.doc.screen/topic/screen_8h_1Screen_Property_Types.html
- https://support7.qnx.com/download/download/26216/Application_and_Window_Management.pdf
- https://www.qnx.com/download/download/26204/QNX_CAR_Architecture_Guide.pdf
- https://support7.qnx.com/download/download/26214/QNX_CAR_Users_Guide.pdf
