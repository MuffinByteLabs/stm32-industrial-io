# Project maintenance scripts

## Candidate reference sync

I use [sync_reference_datasheets.py](sync_reference_datasheets.py) to maintain the PDFs listed in my [reference manifest](../references/datasheets/manifest.json). The script downloads the recorded source URLs over HTTPS and checks PDF identity. I run it with Python 3.12 and the dependency in [requirements-dev.txt](../requirements-dev.txt).

~~~text
python scripts/sync_reference_datasheets.py
~~~

I use --refresh when I intend to redownload existing references. Server or network failures can leave a reference unavailable; the manifest records the outcome explicitly.

My identity checks require a parseable PDF and the expected family identifier on an early page. I record page count, byte length, hash, source, and check time. Exact-package pin review, current-revision verification, and circuit validation are separate work.

## Repository audit

I use [audit_project.py](audit_project.py) to check local Markdown links/anchors, saved candidate PDF hashes and identity, archived capacitor CSV hashes/headers/sample summaries, native-project locations, and project-relative library paths.

~~~text
python scripts/audit_project.py
~~~

An unavailable reference is reported as a warning when its manifest status says it is missing. A PDF claimed as downloaded but absent or changed fails the audit. The script reports native design availability; it does not run ERC, DRC, simulations, or physical tests.

I keep selected numerical assumptions in my [engineering calculations](../docs/calcs/README.md). The [KiCad workflow](../.github/workflows/kicad-ci.yml) runs native-design checks once implementation files exist.

I use [audit_component_selections.py](audit_component_selections.py) to check required selection fields, duplicate IDs, retained interface quantities and absence of retired Rev A parts. My documentation workflow also runs the power, rail-support, analog and PWM calculations. These scope checks do not certify electrical connectivity or a released BOM.

My scripts use the repository's pinned dependency rather than a machine-specific runtime path.

## Capture asset availability

I use [audit_capture_readiness.py](audit_capture_readiness.py) to check clean selected CAD identifiers and registered local collections, then list missing symbols/footprints against installed KiCad 10 libraries where available.

~~~text
python scripts/audit_capture_readiness.py
python scripts/audit_capture_readiness.py --require-assets
~~~

The normal report can pass structure checks while explicitly reporting an open asset gate. `--require-assets` fails on missing or unchecked fitted assets. An explicit `--kicad-library-root` points to the directory containing symbols/ and footprints/. Off-board mates and zero-quantity options are outside this fitted-asset check. Neither mode establishes pin/pad, electrical or manufacturing approval; I follow the [library preflight](../docs/Library_Preflight.md) for that evidence.

## Host diagnostics checks

The [diagnostic tool](../tools/diagnostics/README.md) implements the host side of my [protocol contract](../firmware/Protocol.md). Its standard-library tests check framing, CRC/error handling, coherent data decoding and guarded commands against development fixtures.

~~~text
python -m unittest discover -s tools/diagnostics/tests -v
python tools/diagnostics/fieldio_cli.py --simulate identity
python tools/diagnostics/fieldio_cli.py --simulate snapshot
~~~

These checks run in the documentation workflow without a serial driver or physical board. Simulated logs remain marked as development data and cannot be filed as measured [portfolio evidence](../docs/Portfolio_Evidence.md).
