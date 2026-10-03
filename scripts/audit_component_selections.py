"""I audit capture selection coverage; this is not an electrical or sourcing approval."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = ('power.json', 'control_service.json', 'analog.json', 'field_io.json')
FIELDS = ('component_id', 'qty', 'mpn', 'manufacturer', 'value', 'package',
          'kicad_symbol', 'kicad_footprint', 'tolerance', 'rating',
          'datasheet_url', 'purpose', 'evidence', 'status')


def main():
    errors, ids, parts, counts = [], set(), set(), {}
    for name in REQUIRED_FILES:
        path = ROOT / 'docs/components' / name
        if not path.exists():
            errors.append(f'Missing circuit-selection file: {name}')
            continue
        data = json.loads(path.read_text(encoding='utf-8-sig'))
        rows = data.get('components', [])
        if not rows:
            errors.append(f'{name}: no component selections')
        counts[name] = len(rows)
        for row in rows:
            cid = row.get('component_id', '(missing ID)')
            for field in FIELDS:
                if field not in row:
                    errors.append(f'{name}/{cid}: missing {field}')
            if cid in ids:
                errors.append(f'Duplicate component ID: {cid}')
            ids.add(cid)
            if not isinstance(row.get('qty'), int) or row['qty'] < 0:
                errors.append(f'{name}/{cid}: invalid quantity allocation')
            if not row.get('mpn') or not row.get('purpose') or not row.get('evidence'):
                errors.append(f'{name}/{cid}: incomplete ordering/purpose/evidence data')
            parts.add(row.get('mpn'))
    print(json.dumps({'scope':'Selection-index structure and block coverage only; not a released BOM, inventory, library or electrical approval',
                      'groups_by_block':counts,'component_groups':len(ids),
                      'unique_order_codes':len(parts),'failures':errors},indent=2))
    return bool(errors)


if __name__ == '__main__':
    raise SystemExit(main())
