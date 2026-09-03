# 01 - System Goal

## Goal

Create a modernized infotainment experience for a 2014 Jeep Grand Cherokee WK2 with RA4 that visually and functionally resembles newer Uconnect generations while preserving factory vehicle functions.

## Required user experience

The driver should be able to:

- Boot into a modern Jeep/Uconnect-inspired home screen.
- Connect an Android phone and use native Android Auto.
- Connect an iPhone and use native Apple CarPlay.
- Open Jeep controls at any time without losing vehicle functionality.
- Control heated seats, heated steering wheel, HVAC and supported comfort features.
- Retain the factory backup camera, vehicle settings, steering-wheel controls and audio system.
- Return to the original RA4 UI as a fallback/service mode.

## Design principle

The stock RA4 remains the authority for Jeep-specific behavior. The modernization layer should integrate with existing high-level RA4 services instead of reimplementing vehicle logic or safety-critical CAN behavior.

## Display constraint

The factory HMI targets 640x480. The new UI should be designed specifically for that resolution rather than shrinking a later Uconnect interface pixel-for-pixel.

## Non-goals

- Porting a complete later UAS/UAQ firmware image to RA4 hardware.
- Circumventing FCA/Harman update signing.
- Replacing safety-critical vehicle control logic.
- Requiring a second dashboard-mounted display.
