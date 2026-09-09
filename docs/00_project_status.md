# Project status: blocked without manufacturer support

Updated: 2026-09-07.

**The original software-only CarPlay/Android Auto integration goal is effectively
not achievable with the hardware, software and authorization available to this
project. Implementation is on hold.** A viable authorized route would require
manufacturer-provided or manufacturer-approved development/service hardware,
the corresponding access and credentials, and supported software and licensing.
None of that has been established as available to this project.

This is the project's practical feasibility conclusion for stock RA4 / VP4
18.45.01. We have not established a viable legal, manufacturer-authorized way to
deliver the proposed integration. It is not a legal determination that every
independent modification is unlawful, nor proof that a particular manufacturer
tool would make this possible. No specific purchasable tool or supported retrofit
has been identified as sufficient.

## Why the project is blocked

- **Service access is controlled externally.** Opening the engineering menu or
  possessing the radio's anti-theft PIN does not grant development access.
  Service authorization uses an authentically issued, radio-bound certificate
  and a separate diagnostic authorization boundary. See the
  [security findings](../reports/MASTER_FINDINGS.md) and
  [service-certificate transport report](../reports/service_certificate_diagnostic_transport.md).
- **Building an application does not make it installable.** The Hello Uconnect
  host artifact has no issued application identity, accepted signing envelope,
  or policy/DRM grant. Recovering the package schema does not supply the issuer,
  credentials or permission to deploy it. See the
  [installability gap](../reports/hello_installability_gap.md).
- **Projection references are not a working implementation.** Stock strings and
  UI branches do not establish a complete installed screen/backend, a compatible
  licensed engine, or supported interfaces. See the
  [placement analysis](16_ra4_resident_placement_decision.md) and
  [engine feasibility screen](11_projection_engine_feasibility.md).
- **Physical transport and runtime behavior remain unproved.** Dual-role USB
  silicon does not establish the installed phone-port route, drivers, hub/VBUS
  behavior or a functioning projection transport. See the
  [transport gate matrix](20_projection_transport_gate_matrix.md).

Manufacturer hardware alone would not resolve signing, entitlements, compatible
software, or projection licensing. More static analysis, an ordinary USB adapter,
a spare radio, or a successful PC prototype does not supply those prerequisites.
Resource limits remain unmeasured; this decision is not a claim that the processor
has been proved incapable of projection.

## What remains useful

The repository preserves read-only findings, original host prototypes and
analysis tools. They document what was learned and can be inspected or exercised
locally. They are not a flashable upgrade, installable radio application, working
CarPlay/Android Auto receiver, or a supported retrofit procedure.

Earlier architecture documents, implementation plans and target-proof checklists
are retained as conditional research references. Their proposed next steps do
not represent an active deployment roadmap. This status supersedes earlier
resident-first and software-only implementation priorities.

## Conditions for reopening implementation

1. Establish a supported route with the manufacturer or an authorized supplier,
   including availability and permitted use of the required development/service
   hardware and tools. No suitable kit is currently confirmed.
2. Obtain the corresponding legitimate application/service authorization,
   signing or packaging service, identity, policy and entitlement support.
3. Establish a compatible, licensed projection engine and supported RA4 display,
   audio, USB and application integration contracts.
4. Only then define an owner-authorized spare-bench validation and recovery plan,
   with resource measurements and preservation of factory functions.

Until those prerequisites exist, do not resume radio deployment work or present
additional reverse engineering as a way around manufacturer authorization.
Signing bypasses, credential forgery and repurposing anti-theft authorization
remain outside project scope.
