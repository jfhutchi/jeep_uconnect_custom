"""Build the bounded KIM19/common-base Performance export consumer census.

The scanner parses archive bytes only. Invocation rows are syntactic JVM
references; they do not establish runtime dispatch, service activation, or a
target grant. Output exposes allowlisted match terms and hashes, never complete
unreviewed vendor literals.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
from io import BytesIO
import json
from pathlib import Path
from zipfile import BadZipFile, ZipFile

from analysis_tools.java_classfile import parse_class


REPORT = Path("reports/kim19_runtime_analysis/performance_pages_consumer_census.json")
XLETS = Path("secondary_iso/usr/share/XLETS")
RESOURCE_SUFFIXES = {".cfg", ".conf", ".json", ".mf", ".properties", ".txt", ".xml"}
MATCH_TERMS = ("/fs/usb0", "/mnt/sd0", "timersresult", ".html", "text/html", "file://")
SAFE_EXACT_VALUES = {"/fs/usb0", "/fs/usb0/", "/mnt/sd0", "timersResult", ".html", "text/html"}
PERFORMANCE_PREFIX = "com/sprint/gskills/"
TARGETS = {
    "performance_writer": ({"com/sprint/gskills/controller/savetimerrun/TimerSavingData"}, {"saveDataTo", "createUpdateDownloadFile", "updateHTML"}),
    "store_base64_file_helpers": ({"com/sprint/chrysler/storefront/communications/Base64"}, {"decodeFromFile", "decodeToFile", "decodeFileToFile", "encodeFromFile", "encodeToFile", "encodeFileToFile"}),
    "kona_ecodrive": ({"kona/ecoDrive/EcoDrive", "kona/ecoDrive/EcoDriveImpl", "kona/ecoDrive/EcoDriveManager"}, {"getEcoDrive", "startUSBTransfer", "getListOfDataFiles", "getFileByName"}),
    "kona_fileio": ({"kona/fileio/FileIOManager", "com/harman/fileio/FileIOManagerImpl"}, {"getInstance", "getWriteAccess", "startFileIoOperations", "stopFileIoOperations"}),
}
FILE_READER_TYPES = ("java/io/BufferedInputStream", "java/io/BufferedReader", "java/io/FileInputStream", "java/io/FileReader", "java/io/InputStreamReader", "java/io/RandomAccessFile")
FILE_READ_NAMES = {"open", "read", "readLine", "list", "listFiles"}
VIEW_TOKENS = ("filechooser", "browser", "webview", "html", "mime")
TRANSFER_TOKENS = ("import", "export", "copy", "transfer", "upload")
MEDIA_TOKENS = ("usb", "sdcard", "removable", "media")
NOTIFY_TOKENS = ("listener", "status", "notify", "insert", "remove", "mount", "eject")
LAUNCH_NAMES = {"chain", "launch", "launchApplication", "startApplication", "startXlet"}


def encode(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True, allow_nan=False) + "\n").encode("ascii")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def discover_sources(corpus: Path) -> tuple[list[Path], int, int]:
    root = corpus.resolve(strict=True)
    kim = sorted((root / XLETS / "kim_packages/KIM19").rglob("*.jar"))
    common = sorted((root / XLETS / "base").rglob("*.jar"))
    if len(kim) != 19 or len(common) != 4:
        raise ValueError(f"reviewed census expects 19 KIM19 and 4 common-base JARs, found {len(kim)} and {len(common)}")
    for source in kim + common:
        source.resolve(strict=True).relative_to(root)
    return kim + common, len(kim), len(common)


def matched_terms(value: str) -> list[str]:
    lowered = value.lower()
    return [term for term in MATCH_TERMS if term in lowered]


def literal_evidence(value: str) -> dict | None:
    matches = matched_terms(value)
    if not matches:
        return None
    row = {"matched_terms": matches, "value_sha256": digest(value.encode("utf-8")), "value_length": len(value)}
    if value in SAFE_EXACT_VALUES:
        row["reviewed_exact_value"] = value
    return row


def classify_edge(owner: str, name: str, descriptor: str) -> list[str]:
    categories = []
    for target_id, (owners, names) in TARGETS.items():
        if owner in owners and name in names:
            categories.append(target_id)
    joined = f"{owner} {name}".lower()
    if owner in FILE_READER_TYPES or name in FILE_READ_NAMES:
        categories.append("file_open_read_enumerate")
    if any(token in joined for token in VIEW_TOKENS):
        categories.append("chooser_browser_webview_html_mime")
    transfer = any(token in joined for token in ("import", "export", "transfer", "upload"))
    copy_or_scan = any(token in name.lower() for token in ("copy", "scan")) and any(token in owner.lower() for token in ("file", "storage", "media", "usb", "sd"))
    if transfer or copy_or_scan:
        categories.append("media_scan_import_export_copy_transfer")
    if any(token in joined for token in MEDIA_TOKENS) and any(token in joined for token in NOTIFY_TOKENS):
        categories.append("usb_sd_media_notification")
    if name in LAUNCH_NAMES or ("appmanager" in owner.lower() and "launch" in name.lower()):
        categories.append("application_launcher")
    return sorted(set(categories))


def scan_sources(root: Path, sources: list[Path], *, kim_count: int, common_count: int) -> dict:
    root = root.resolve(strict=True)
    artifacts = []
    initial_hashes = {}
    literal_rows = []
    resource_rows = []
    invocation_rows = []
    class_count = 0
    for jar_path in sources:
        relative = jar_path.resolve(strict=True).relative_to(root).as_posix()
        jar_bytes = jar_path.read_bytes()
        initial_hashes[jar_path] = digest(jar_bytes)
        try:
            archive = ZipFile(BytesIO(jar_bytes))
        except BadZipFile as exc:
            raise ValueError(f"invalid JAR: {relative}") from exc
        with archive:
            names = [info.filename for info in archive.infolist()]
            duplicates = sorted(name for name, count in Counter(names).items() if count != 1)
            if duplicates:
                raise ValueError(f"duplicate archive member in {relative}: {duplicates[0]}")
            class_names = sorted(name for name in names if name.endswith(".class"))
            class_count += len(class_names)
            artifacts.append({"path": relative, "bytes": len(jar_bytes), "sha256": initial_hashes[jar_path], "class_entries": len(class_names)})
            for member in sorted(names):
                if Path(member).suffix.lower() not in RESOURCE_SUFFIXES:
                    continue
                data = archive.read(member)
                for line_number, line in enumerate(data.decode("latin-1", errors="replace").splitlines(), 1):
                    evidence = literal_evidence(line)
                    if evidence:
                        resource_rows.append({"source": relative, "member": member, "member_sha256": digest(data), "line_number": line_number, **evidence})
            for member in class_names:
                data = archive.read(member)
                try:
                    model = parse_class(data)
                except ValueError as exc:
                    raise ValueError(f"class parse failure in {relative}!/{member}: {exc}") from exc
                class_sha256 = digest(data)
                for method in model.methods:
                    for literal in method.literal_edges:
                        if not isinstance(literal.value, str):
                            continue
                        evidence = literal_evidence(literal.value)
                        if evidence:
                            literal_rows.append({"source": relative, "class_name": model.name, "class_sha256": class_sha256, "method_name": method.name, "descriptor": method.descriptor, "bci": literal.offset, "opcode": literal.opcode, **evidence})
                    for edge in method.member_edges:
                        categories = classify_edge(edge.owner, edge.name, edge.descriptor)
                        if categories:
                            invocation_rows.append({"categories": categories, "source": relative, "class_name": model.name, "class_sha256": class_sha256, "method_name": method.name, "descriptor": method.descriptor, "bci": edge.offset, "opcode": edge.opcode, "owner": edge.owner, "name": edge.name, "target_descriptor": edge.descriptor, "self_reference": model.name == edge.owner})
    for jar_path, expected in initial_hashes.items():
        if digest(jar_path.read_bytes()) != expected:
            raise ValueError(f"source changed during census: {jar_path.relative_to(root).as_posix()}")

    def has_category(row: dict, category: str) -> bool:
        return category in row["categories"]
    non_perf_identity = [row for row in literal_rows if any(term in row["matched_terms"] for term in ("/fs/usb0", "/mnt/sd0", "timersresult")) and not row["class_name"].startswith(PERFORMANCE_PREFIX)]
    non_perf_kim_html = [row for row in literal_rows if any(term in row["matched_terms"] for term in (".html", "text/html", "file://")) and "/kim_packages/KIM19/" in "/" + row["source"] and not row["class_name"].startswith(PERFORMANCE_PREFIX)]
    writer_callers = [row for row in invocation_rows if has_category(row, "performance_writer") and not row["class_name"].startswith(PERFORMANCE_PREFIX)]
    store_external = [row for row in invocation_rows if has_category(row, "store_base64_file_helpers") and not row["self_reference"]]
    kim_ecodrive = [row for row in invocation_rows if has_category(row, "kona_ecodrive") and "/kim_packages/KIM19/" in "/" + row["source"]]
    kim_fileio = [row for row in invocation_rows if has_category(row, "kona_fileio") and "/kim_packages/KIM19/" in "/" + row["source"]]
    exact_candidate_count = sum(map(len, (non_perf_identity, non_perf_kim_html, writer_callers, store_external, kim_ecodrive, kim_fileio)))
    category_counts = Counter(category for row in invocation_rows for category in row["categories"])
    conclusion = ("One or more syntactic candidates matched the reviewed Performance storage/format/service predicates; no complete handoff is inferred automatically." if exact_candidate_count else "No direct syntactic handoff matched the reviewed Performance storage identities, KIM19 HTML/file URI literals, writer calls, or selected service/helper calls; broader candidate API references remain separately enumerated.")
    return {
        "schema_version": 2,
        "scope": "All 19 KIM19 JARs plus four nearby common-base JARs; static references and syntactic invocation edges only",
        "evidence_label": "PROVED",
        "artifacts": artifacts,
        "coverage": {"kim19_jars": kim_count, "common_base_jars": common_count, "total_jars": len(artifacts), "class_entries": class_count, "class_parse_errors": 0},
        "literal_match_policy": {"case_insensitive_substrings": list(MATCH_TERMS), "disclosure": "Only matched allowlist terms, length, hash, and reviewed exact values are emitted."},
        "allowlisted_class_literal_matches": literal_rows,
        "allowlisted_resource_line_matches": resource_rows,
        "candidate_api_invocations": invocation_rows,
        "candidate_api_category_counts": dict(sorted(category_counts.items())),
        "scoped_consumer_result": {
            "non_performance_storage_identity_literal_count": len(non_perf_identity),
            "non_performance_kim_html_or_file_uri_literal_count": len(non_perf_kim_html),
            "non_performance_performance_writer_caller_count": len(writer_callers),
            "store_base64_external_file_helper_caller_count": len(store_external),
            "kim19_ecodrive_caller_count": len(kim_ecodrive),
            "kim19_kona_fileio_caller_count": len(kim_fileio),
            "reviewed_exact_candidate_count": exact_candidate_count,
            "conclusion": conclusion,
            "runtime_reachability": "UNKNOWN: syntactic matches or their absence do not prove a complete runtime handoff or global target absence.",
        },
    }


def build_report(corpus: Path) -> dict:
    root = corpus.resolve(strict=True)
    sources, kim_count, common_count = discover_sources(root)
    return scan_sources(root, sources, kim_count=kim_count, common_count=common_count)


def write_or_check(output: Path, report: dict, check: bool) -> int:
    expected = encode(report)
    if check:
        return 0 if output.is_file() and output.read_bytes() == expected else 1
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(expected)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", required=True, type=Path)
    parser.add_argument("--output", type=Path, default=REPORT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    corpus = args.corpus.resolve(strict=True)
    if args.output.resolve().is_relative_to(corpus):
        parser.error("output must be outside recovered corpus")
    result = write_or_check(args.output, build_report(corpus), args.check)
    print("Performance consumer census " + ("verified" if args.check and not result else "stale" if result else "written"))
    return result


if __name__ == "__main__":
    raise SystemExit(main())
