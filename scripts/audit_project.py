"""Check documents/assets; successful results do not validate hardware."""

from __future__ import annotations

from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re
from urllib.parse import unquote

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
IGNORED = {".git", ".agents", ".codex", ".aws", "__pycache__", ".venv", "out"}
PROJECT_VARIABLE = "$" + "{KIPRJMOD}"


def project_files() -> list[Path]:
    result = []
    for directory, folders, files in os.walk(ROOT):
        folders[:] = [name for name in folders if name not in IGNORED]
        result.extend(Path(directory) / name for name in files)
    return result


def without_fences(text: str) -> str:
    fence = chr(96) * 3
    return re.sub(rf"(?ms)^{fence}.*?^{fence}[^\n]*\n?|^~~~.*?^~~~[^\n]*\n?", "", text)


def anchors(text: str) -> set[str]:
    result = set(re.findall(r'<a\s+(?:id|name)=["\']([^"\']+)', text))
    seen = Counter()
    for heading in re.findall(r"(?m)^#{1,6}\s+(.+?)\s*#*\s*$", without_fences(text)):
        heading = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", heading)
        slug = re.sub(r"[^\w\-\s]", "", heading.lower())
        slug = re.sub(r"\s", "-", slug)
        result.add(slug + ("" if not seen[slug] else f"-{seen[slug]}"))
        seen[slug] += 1
    return result


def main() -> int:
    failures, warnings = [], []
    files = project_files()
    markdown = [p for p in files if p.suffix == ".md"]
    local_links = 0
    for path in markdown:
        body = without_fences(path.read_text(encoding="utf-8-sig"))
        for match in re.finditer(r"!?\[[^\]]*\]\((<[^>]+>|[^)\s]+)\)", body):
            target = match.group(1).strip("<>")
            if re.match(r"^[a-z][a-z0-9+.-]+:", target, re.I) and not re.match(r"^[A-Z]:[/\\]", target, re.I):
                continue
            if target.startswith("//"):
                continue
            destination, _, fragment = unquote(target).partition("#")
            destination = destination.split("?", 1)[0]
            # Codex file links may append a one-based line/column.
            destination = re.sub(r":\d+(?::\d+)?$", "", destination)
            linked = Path(destination) if Path(destination).is_absolute() else path.parent / destination
            linked = linked.resolve()
            local_links += 1
            if not linked.exists():
                failures.append(f"{path.relative_to(ROOT)}: missing link {target}")
            elif fragment and linked.suffix == ".md" and fragment not in anchors(linked.read_text(encoding="utf-8-sig")):
                failures.append(f"{path.relative_to(ROOT)}: missing anchor {target}")

    manifest = json.loads((ROOT / "references/datasheets/manifest.json").read_text(encoding="utf-8-sig"))
    checked_pdfs = 0
    for mpn, part in manifest["parts"].items():
        if part.get("status") != "downloaded_identity_checked":
            warnings.append(f"{mpn}: local PDF unavailable; see manifest status and manufacturer URL")
            continue
        path = ROOT / "references/datasheets" / part["file"]
        if not path.is_file():
            failures.append(f"{mpn}: manifest claims an absent PDF")
            continue
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != part["sha256"] or len(data) != part["bytes"]:
            failures.append(f"{mpn}: PDF hash/length differs from manifest")
        reader = PdfReader(path)
        text = "\n".join(page.extract_text() or "" for page in reader.pages[:3])
        if len(reader.pages) != part["pages"] or part["title_token"].lower() not in text.lower():
            failures.append(f"{mpn}: PDF identity/page count differs from manifest")
        checked_pdfs += 1

    migration = json.loads((ROOT / "docs/reviews/migration_manifest.json").read_text(encoding="utf-8-sig"))
    for removed in migration["Removed"]:
        if (ROOT / removed).exists():
            failures.append(f"Superseded target still present: {removed}")
    for old, new in migration["RenamedLibraries"]:
        if (ROOT / old).exists() or not (ROOT / new).is_dir():
            failures.append(f"Library migration incomplete: {old} -> {new}")

    project = ROOT / "hardware/STM32_Industrial_IO"
    native = [p for p in files if p.suffix in {".kicad_pro", ".kicad_sch", ".kicad_pcb"}]
    for path in native:
        if path.parent != project:
            failures.append(f"Unexpected native project path: {path.relative_to(ROOT)}")
    asset_paths = 0
    for path in [project / "fp-lib-table", *(ROOT / "hardware/libs").rglob("*.kicad_mod")]:
        for value in re.findall(r'"(\$[{]KIPRJMOD[}][^"]+)"', path.read_text(encoding="utf-8-sig")):
            if not Path(value.replace(PROJECT_VARIABLE, str(project))).resolve().exists():
                failures.append(f"{path.relative_to(ROOT)}: missing local asset {value}")
            asset_paths += 1

    obsolete = re.compile(r"ESP32S3_FieldIO_Final_Design_Document|board2_calcs|FieldIO_JLC|field_io/secrets|VLOAD\+|OTA in the field")
    for path in markdown:
        if "reviews" not in path.parts and obsolete.search(path.read_text(encoding="utf-8-sig")):
            failures.append(f"Active legacy contract in {path.relative_to(ROOT)}")

    print(json.dumps({
        "scope": "Document/link/reference/library migration checks only",
        "markdown_files": len(markdown),
        "local_links_checked": local_links,
        "candidate_pdfs_identity_hash_checked": checked_pdfs,
        "project_relative_assets_checked": asset_paths,
        "native_design_files": len(native),
        "warnings": warnings,
        "failures": failures,
    }, indent=2))
    return bool(failures)


if __name__ == "__main__":
    raise SystemExit(main())
