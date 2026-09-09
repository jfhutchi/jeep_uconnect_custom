NOT TARGET VERIFIED. This is a host-executable protocol model. It is not an
RA4 binary, has no target authorization route, and proves neither cabin-hub
transport nor physical AOA operation.

# RA4 AOA Host Model

This directory exists only because the evidence-gated Phase-7 decision is B. It
models the exact Android Open Accessory control sequence, detach/re-enumeration,
accessory endpoint selection, cleanup, and one bounded deterministic bulk frame
in each direction against a scripted mock USB host. It deliberately has no
libusb, QNX, RA4 packaging, deployment, or Android Auto projection dependency.

Run the host tests from the repository root:

```powershell
python -m unittest discover -s prototype\ra4_aoa_probe\tests -v
```

Passing tests establish only deterministic state-machine behavior. Physical
success still requires every criterion in `docs/ra4_aoa_transport.md` to be
observed on authorized hardware.
