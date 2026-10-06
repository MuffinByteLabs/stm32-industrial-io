"""Report selected CAD asset availability without claiming package approval."""
import argparse
import json
import os
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / 'hardware/STM32_Industrial_IO'
SELECTIONS = ('power.json', 'control_service.json', 'analog.json', 'field_io.json')
IDENTIFIER = re.compile(r'^[A-Za-z0-9_.+-]+:[^\s:()\\/]+$')


def table_paths(filename):
    body = (PROJECT / filename).read_text(encoding='utf-8-sig')
    entries = re.findall(r'\(lib\s+\(name\s+"([^"]+)"\).*?\(uri\s+"([^"]+)"\)',
                         body, flags=re.S)
    return {name: Path(uri.replace('${KIPRJMOD}', str(PROJECT))).resolve()
            for name, uri in entries}


def find_stock_root(explicit):
    if explicit:
        return Path(explicit).expanduser().resolve()
    configured = os.environ.get('KICAD10_SYMBOL_DIR')
    candidates = ([Path(configured).parent] if configured else [])
    candidates.extend((Path('C:/Program Files/KiCad/10.0/share/kicad'),
                       Path('/usr/share/kicad'), Path('/usr/local/share/kicad')))
    return next((path for path in candidates if (path / 'symbols').is_dir()
                 and (path / 'footprints').is_dir()), None)


def has_symbol(path, name):
    if not path.is_file():
        return False
    body = path.read_text(encoding='utf-8-sig')
    return bool(re.search(r'\(symbol\s+"' + re.escape(name) + r'"\s', body))


def inspect(identifier, kind, local, stock):
    if not isinstance(identifier, str) or not IDENTIFIER.fullmatch(identifier):
        return {'identifier': identifier, 'availability': 'invalid_identifier'}
    library, asset = identifier.split(':', 1)
    is_local = library in local
    if is_local:
        container = local[library]
    elif stock is not None:
        container = (stock / 'symbols' / (library + '.kicad_sym') if kind == 'symbol'
                     else stock / 'footprints' / (library + '.pretty'))
    else:
        return {'identifier': identifier, 'availability': 'stock_libraries_not_available',
                'package_approval': 'not_established_by_this_audit'}
    present = (has_symbol(container, asset) if kind == 'symbol'
               else (container / (asset + '.kicad_mod')).is_file())
    return {'identifier': identifier,
            'availability': ('present' if present else 'missing'),
            'source': ('project_local' if is_local else 'installed_stock'),
            'package_approval': 'not_established_by_this_audit'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kicad-library-root', help='Directory containing symbols/ and footprints/')
    parser.add_argument('--require-assets', action='store_true',
                        help='Fail if selected assets are missing or their availability cannot be checked')
    args = parser.parse_args()
    stock = find_stock_root(args.kicad_library_root)
    local_symbols = table_paths('sym-lib-table')
    local_footprints = table_paths('fp-lib-table')
    failures, rows = [], []
    if args.kicad_library_root and (not stock.is_dir() or not (stock / 'symbols').is_dir()
                                   or not (stock / 'footprints').is_dir()):
        failures.append('Explicit KiCad library root must contain symbols/ and footprints/')
        stock = None
    for kind, libraries in (('symbol', local_symbols), ('footprint', local_footprints)):
        for name, path in libraries.items():
            if not path.exists():
                failures.append(f'Registered local {kind} collection {name} is absent')
    for filename in SELECTIONS:
        data = json.loads((ROOT / 'docs/components' / filename).read_text(encoding='utf-8-sig'))
        for part in data['components']:
            # Mating plugs remain off-board purchases. Zero-quantity options are not fitted allocations.
            if part['qty'] <= 0 or part['status'] == 'selected_accessory' or part.get('group') == 'off_board':
                continue
            row = {'selection': filename, 'component_id': part['component_id'], 'mpn': part['mpn'],
                   'symbol': inspect(part['kicad_symbol'], 'symbol', local_symbols, stock),
                   'footprint': inspect(part['kicad_footprint'], 'footprint', local_footprints, stock)}
            for kind in ('symbol', 'footprint'):
                state = row[kind]['availability']
                if state == 'invalid_identifier' or (args.require_assets and state != 'present'):
                    failures.append(f"{filename}/{part['component_id']}: {kind} {state}")
            rows.append(row)
    missing = [row for row in rows if any(row[kind]['availability'] == 'missing'
                                          for kind in ('symbol', 'footprint'))]
    unchecked = [row for row in rows if any(row[kind]['availability'] == 'stock_libraries_not_available'
                                            for kind in ('symbol', 'footprint'))]
    native = {suffix: (PROJECT / ('STM32_Industrial_IO.' + suffix)).is_file()
              for suffix in ('kicad_pro', 'kicad_sch', 'kicad_pcb')}
    print(json.dumps({'scope': 'Selected positive-quantity board asset availability; existence is not pin/pad or electrical approval',
                      'stock_library_root': str(stock) if stock else None,
                      'groups_checked': len(rows), 'groups_with_missing_assets': len(missing),
                      'groups_with_unchecked_stock_assets': len(unchecked),
                      'native_files_present': native,
                      'capture_asset_gate': 'open' if missing or unchecked or failures else 'assets_present_package_approval_still_required',
                      'missing_asset_groups': missing, 'unchecked_stock_groups': unchecked,
                      'failures': failures}, indent=2))
    return bool(failures)


if __name__ == '__main__':
    raise SystemExit(main())
