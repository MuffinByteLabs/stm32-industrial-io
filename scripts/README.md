# Project maintenance scripts

## Candidate reference sync

[sync_reference_datasheets.py](sync_reference_datasheets.py) maintains PDFs listed in [the manifest](../references/datasheets/manifest.json). It can use the installed DigiKey skill's direct manufacturer-URL downloader or Python HTTPS. It needs Python with pypdf.

~~~text
python scripts/sync_reference_datasheets.py
~~~

Optional arguments are --skill-downloader with the path to fetch_datasheet_digikey.py and --refresh to redownload existing references. Network restrictions or manufacturer server failures can leave a reference unavailable; the manifest records failures explicitly.

Downloaded files must parse as PDFs and contain the expected family identifier on an early page. The manifest stores page count, byte length, hash, source, and check time. These are document identity checks. Package/pin extraction and circuit verification are separate pending work.

## Repository audit

[audit_project.py](audit_project.py) checks local Markdown links/anchors, candidate PDF hashes/identity, removed legacy targets, new library paths, and common obsolete contract strings. It also needs pypdf.

~~~text
python scripts/audit_project.py
~~~

Missing remote references are reported as warnings if their manifest status already says they are unavailable. An absent PDF falsely claimed as downloaded fails the audit. The script reports native design availability but does not run ERC, DRC, simulations, or physical tests.

Use [the planning calculations](../docs/calcs/README.md) for numerical assumptions. CI owns future native KiCad checks after implementation exists.

On this desktop, the bundled workspace Python can provide pypdf if the system Python does not. Keep machine-specific runtime paths out of project build configuration.
