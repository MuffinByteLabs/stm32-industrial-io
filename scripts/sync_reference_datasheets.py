"""Maintain the candidate-family PDFs listed in the project manifest.

I use standard-library HTTPS to retrieve manufacturer reference documents.
A valid PDF and first-page family match
establish document identity only, never schematic or package correctness.
Run with a Python runtime containing pypdf for identity verification.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import urllib.request

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "references" / "datasheets"
MANIFEST = DIRECTORY / "manifest.json"


def retrieve(item: tuple[str, dict], refresh: bool) -> tuple[str, dict]:
    mpn, part = item
    result = dict(part)
    target = DIRECTORY / part["file"]
    temporary = target.with_suffix(".download.tmp")
    try:
        if refresh or not target.exists():
            request = urllib.request.Request(
                part["datasheet_url"],
                headers={"User-Agent": "Mozilla/5.0"},
            )
            with urllib.request.urlopen(request, timeout=20) as response:
                temporary.write_bytes(response.read())
            if not temporary.read_bytes().startswith(b"%PDF"):
                raise ValueError("response is not a PDF")
            candidate = temporary
        else:
            candidate = target
        reader = PdfReader(candidate)
        first_pages = "\n".join(page.extract_text() or "" for page in reader.pages[:3])
        if part["title_token"].lower() not in first_pages.lower():
            raise ValueError("expected component family absent from first three PDF pages")
        page_count = len(reader.pages)
        digest = hashlib.sha256(candidate.read_bytes()).hexdigest()
        if candidate == temporary:
            temporary.replace(target)
        result.update(
            status="downloaded_identity_checked",
            pages=page_count,
            bytes=target.stat().st_size,
            sha256=digest,
            checked_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"),
            verification_scope="PDF parses and family token appears in first three pages; electrical/pin extraction pending",
        )
        result.pop("error", None)
    except Exception as exc:
        temporary.unlink(missing_ok=True)
        result.update(status="download_failed", error=f"{type(exc).__name__}: {exc}")
    return mpn, result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    items = list(manifest["parts"].items())
    with ThreadPoolExecutor(max_workers=4) as pool:
        pending = [pool.submit(retrieve, item, args.refresh) for item in items]
        for future in as_completed(pending):
            mpn, result = future.result()
            manifest["parts"][mpn] = result
            print(json.dumps({"part": mpn, "status": result["status"], "error": result.get("error")}), flush=True)
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    failures = [mpn for mpn, part in manifest["parts"].items() if part["status"] == "download_failed"]
    print(json.dumps({"documents": len(items), "failed": failures}), flush=True)
    return bool(failures)


if __name__ == "__main__":
    raise SystemExit(main())
