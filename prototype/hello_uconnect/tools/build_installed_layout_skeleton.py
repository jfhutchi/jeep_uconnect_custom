"""Build a host-only model of the proved RA4 factory installed layout."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePath
import re

from analysis_tools.resident_package_inspect import is_safe_leaf_name, parse_java_properties


STATUS = "UNSIGNED / NON-INSTALLABLE / RESEARCH ARTIFACT"
_SAFE_LEAF = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build_installed_layout_skeleton(
    application_jar: Path, descriptor: Path, output_root: Path
) -> dict[str, object]:
    """Create only the proved installed-layout files; never fabricate key.jar."""

    application_jar = Path(application_jar)
    descriptor = Path(descriptor)
    output_root = Path(output_root)
    if not application_jar.is_file() or not descriptor.is_file():
        raise ValueError("application JAR and descriptor must exist")
    if output_root.exists():
        raise ValueError("output directory already exists")

    descriptor_data = descriptor.read_bytes()
    properties = parse_java_properties(descriptor_data)
    app_id = properties.get("xlet.appId", "")
    jar_file = properties.get("xlet.jarFile", "")
    if (
        not app_id
        or app_id in (".", "..")
        or PurePath(app_id).name != app_id
        or not _SAFE_LEAF.fullmatch(app_id)
    ):
        raise ValueError("xlet.appId is not a safe directory name")
    if (
        not jar_file
        or not is_safe_leaf_name(jar_file)
        or not _SAFE_LEAF.fullmatch(jar_file)
        or not jar_file.lower().endswith(".jar")
    ):
        raise ValueError("xlet.jarFile is not a safe JAR filename")

    jars = output_root / app_id / "prog" / "jars"
    jars.mkdir(parents=True)
    files = {
        Path(app_id) / "prog" / "jars" / jar_file: application_jar.read_bytes(),
        Path(app_id) / "prog" / "jars" / "magic.txt": b"HB_CMC",
        Path(app_id) / "prog" / "xlet.properties": descriptor_data,
        Path("RESEARCH-STATUS.txt"): (
            STATUS
            + "\n\n"
            + "This directory models only the proved factory installed layout.\n"
            + "It is not an accepted incoming RA4 package and must not be installed.\n"
            + "The payload-root signed descriptor, legitimate prog/jars/key.jar, signer\n"
            + "identity, policy/DRM grant, installer authorization and target acceptance\n"
            + "are absent.\n"
        ).encode("ascii"),
    }
    for relative, data in sorted(files.items(), key=lambda item: item[0].as_posix()):
        destination = output_root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)

    inventory = [
        {
            "name": relative.as_posix(),
            "sha256": _sha256(data),
            "size": len(data),
        }
        for relative, data in sorted(files.items(), key=lambda item: item[0].as_posix())
    ]
    report: dict[str, object] = {
        "app_id": app_id,
        "classification": "incomplete-installed-layout-skeleton",
        "files": inventory,
        "installable": False,
        "missing": ["payload JAR root xlet.properties", "prog/jars/key.jar"],
        "status": STATUS,
    }
    (output_root / "SKELETON-INVENTORY.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="ascii"
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build an unsigned host-only RA4 installed-layout research skeleton"
    )
    parser.add_argument("application_jar", type=Path)
    parser.add_argument("descriptor", type=Path)
    parser.add_argument("output_root", type=Path)
    args = parser.parse_args()
    try:
        report = build_installed_layout_skeleton(
            args.application_jar, args.descriptor, args.output_root
        )
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
