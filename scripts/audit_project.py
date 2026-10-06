"""Check documents/assets; successful results do not validate hardware."""

from __future__ import annotations

from collections import Counter
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import re
from urllib.parse import unquote

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
IGNORED = {".git", ".agents", ".codex", ".aws", "__pycache__", ".venv", "out",
           "output", "tmp_build"}
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
            # Local file links may append a one-based line/column.
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

    capacitor_root = ROOT / "references/capacitors"
    capacitor_manifest = json.loads((capacitor_root / "manifest.json").read_text(encoding="utf-8-sig"))
    checked_capacitor_csvs = 0
    for record in capacitor_manifest["files"]:
        path = capacitor_root / record["file"]
        if not path.is_file():
            failures.append(f"{record['file']}: capacitor manifest claims an absent CSV")
            continue
        payload = path.read_bytes()
        if hashlib.sha256(payload).hexdigest() != record["sha256"] or len(payload) != record["bytes"]:
            failures.append(f"{record['file']}: CSV hash/length differs from manifest")
        rows = list(csv.reader(io.StringIO(payload.decode("utf-8-sig"))))
        headers = [row[0] for row in rows if row and row[0].startswith("#")]
        if headers != record["csv_headers"] or f"#{record['exported_base_model']}" not in headers:
            failures.append(f"{record['file']}: manufacturer CSV identity/headers differ from manifest")
        points = []
        for row in rows:
            try:
                points.append((float(row[0]), float(row[1])))
            except (ValueError, IndexError):
                continue
        if len(points) != record["point_count"]:
            failures.append(f"{record['file']}: CSV point count differs from manifest")
        sample = record.get("sampled_0_50C")
        if sample:
            subset = [(temperature, capacitance) for temperature, capacitance in points if 0 <= temperature <= 50]
            minimum = min(subset, key=lambda point: point[1]) if subset else None
            if (len(subset) != sample["count"] or minimum != (sample["min_temp_C"], sample["min_capacitance_F"])
                    or max((point[1] for point in subset), default=None) != sample["max_capacitance_F"]
                    or any(right[0] - left[0] != sample["step_C"] for left, right in zip(subset, subset[1:]))):
                failures.append(f"{record['file']}: sampled typical temperature summary differs from CSV")
        checked_capacitor_csvs += 1

    pwm_record = ROOT / 'references/reference-designs/pwm_reference.json'
    pwm = json.loads(pwm_record.read_text(encoding='utf-8'))
    pwm_path = pwm_record.parent / pwm['file']
    if not pwm_path.is_file():
        failures.append('PWM guidance: source record claims an absent PDF')
    else:
        payload = pwm_path.read_bytes()
        reader = PdfReader(pwm_path)
        if hashlib.sha256(payload).hexdigest() != pwm['sha256']:
            failures.append('PWM guidance: PDF hash differs from source record')
        if len(reader.pages) != pwm['pages'] or pwm['document_id'] not in (reader.pages[0].extract_text() or ''):
            failures.append('PWM guidance: PDF identity/page count differs from source record')

    project = ROOT / "hardware/STM32_Industrial_IO"
    native = [p for p in files if p.suffix in {".kicad_pro", ".kicad_sch", ".kicad_pcb"}]
    for path in native:
        if path.parent != project:
            failures.append(f"Unexpected native project path: {path.relative_to(ROOT)}")
    asset_paths = 0
    for path in [project / "sym-lib-table", project / "fp-lib-table",
                 *(ROOT / "hardware/libs").rglob("*.kicad_mod")]:
        for value in re.findall(r'"(\$[{]KIPRJMOD[}][^"]+)"', path.read_text(encoding="utf-8-sig")):
            if not Path(value.replace(PROJECT_VARIABLE, str(project))).resolve().exists():
                failures.append(f"{path.relative_to(ROOT)}: missing local asset {value}")
            asset_paths += 1

    print(json.dumps({
        "scope": "Repository document, reference identity, and library checks",
        "markdown_files": len(markdown),
        "local_links_checked": local_links,
        "candidate_pdfs_identity_hash_checked": checked_pdfs,
        "capacitor_csvs_identity_hash_samples_checked": checked_capacitor_csvs,
        "pwm_guidance_pdf_present": pwm_path.is_file(),
        "project_relative_assets_checked": asset_paths,
        "native_design_files": len(native),
        "warnings": warnings,
        "failures": failures,
    }, indent=2))
    return bool(failures)


if __name__ == "__main__":
    raise SystemExit(main())
