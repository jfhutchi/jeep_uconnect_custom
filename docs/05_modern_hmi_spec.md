# 05 - Modern HMI Specification

## Design target

Create a 640x480 interface that feels like a later Jeep/Uconnect system while respecting the physical constraints of the original 8.4-inch RA4 display.

The design should be familiar, automotive, touch-friendly and fast rather than a literal pixel-for-pixel clone of copyrighted production artwork.

## Global layout

### Top status bar

Show only high-value information:

- time
- phone/projection connection state
- audio status
- climate summary where useful

### Main content area

Large touch targets with no desktop-style chrome.

### Persistent bottom app bar

Recommended primary tabs:

- Radio
- Media
- Climate
- Controls
- Phone
- Apps / Projection

A camera control may appear contextually rather than consuming a permanent tab.

## Home

Home should provide two or three configurable cards, for example:

- Now Playing
- Navigation / projection shortcut
- Climate / comfort summary

If projection is active, a prominent return-to-CarPlay/Android-Auto card should be available.

## Radio

Retain factory tuner behavior through RA4 services.

Required:

- AM/FM/SXM where available
- presets
- seek/tune
- station metadata
- steering-wheel control compatibility

## Media

Expose stock media sources and projection-aware sources.

Required:

- USB
- Bluetooth audio
- supported stock sources
- Android Auto
- CarPlay

## Climate

Designed for one-touch access while driving.

Required controls/state:

- driver temperature
- passenger temperature
- fan speed
- vent mode
- AUTO
- A/C
- recirculation
- front defrost
- rear defrost if exposed by stock services
- SYNC where supported

The UI must reflect actual RA4 state rather than assuming commands succeeded.

## Controls

Required vehicle comfort controls:

- driver heated seat
- passenger heated seat
- heated steering wheel
- vented-seat controls where equipped
- additional non-safety vehicle controls only when exposed through documented stock service paths

## Phone

When no projection session is active:

- paired devices
- calls
- contacts where the stock service supports them

When projection is active, defer phone interaction to CarPlay/Android Auto where appropriate.

## Projection

The UI should automatically distinguish the connected platform:

- Android phone -> Android Auto
- iPhone -> CarPlay

Required states:

- no compatible device
- connecting
- loading
- active
- connection error
- user-exited-but-device-still-connected

Projection should support auto-show according to the user preference.

## Camera

The factory camera path has priority over the custom UI.

Requirements:

- automatic reverse-camera takeover remains stock behavior
- no added latency in the reverse-camera path
- return to previous UI after camera exit

## Settings

Organize into:

- Display
- Audio
- Phone / Projection
- Climate / Comfort
- Vehicle
- System

Stock vehicle settings should be surfaced through the stock RA4 service layer, not duplicated with independent CAN logic.

## Interaction rules

- Minimum touch targets should be large enough for use while driving.
- Frequently used actions should require no more than one or two taps.
- Avoid modal dialogs except for genuine errors or safety-relevant confirmation.
- Maintain obvious access back to factory behavior.
- Projection UI should feel native to the phone platform when active; do not skin CarPlay or Android Auto to resemble Jeep.
