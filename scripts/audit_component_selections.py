"""I audit capture selection coverage; this is not an electrical or sourcing approval."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = ('power.json', 'control_service.json', 'analog.json', 'field_io.json')
FIELDS = ('component_id', 'qty', 'mpn', 'manufacturer', 'value', 'package',
          'kicad_symbol', 'kicad_footprint', 'tolerance', 'rating',
          'datasheet_url', 'purpose', 'evidence', 'status')
RETIRED_PARTS = {'TPS2121RUXR', 'TPS2553DBVR', 'LM7705MM/NOPB',
                 'DAC80501ZDGSR', 'OPA2197IDR', 'ADG5401FBCPZ-RL7',
                 'REF3325AIDBZR', 'PMEG3010CEH,115'}
REQUIRED_QUANTITIES = {'STM32G474VET6': 1, 'ADS8684AIDBTR': 1,
                       'ISO1212DBQR': 2, 'TPS4H160BQPWPRQ1': 1,
                       'TPS26611DDFR': 2, 'UCC33421QDHARQ1': 2,
                       'ISO1410DWR': 1, 'ISO1042DWVR': 1}


def main():
    errors, ids, parts, counts, quantities = [], set(), set(), {}, {}
    for name in REQUIRED_FILES:
        path = ROOT / 'docs/components' / name
        if not path.exists():
            errors.append(f'Missing circuit-selection file: {name}')
            continue
        data = json.loads(path.read_text(encoding='utf-8-sig'))
        if name == 'field_io.json':
            pwm = data.get('pwm_scope', {})
            expected_pwm = {'channel': 'DO3', 'frequency_hz': 100,
                            'command_duty_percent': [10, 90],
                            'steady_endpoints_percent': [0, 100],
                            'instantaneous_load_limit_a': 0.5}
            for key, expected in expected_pwm.items():
                if pwm.get(key) != expected:
                    errors.append(f'field_io.json: PWM contract mismatch for {key}')
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
            if row.get('mpn') in RETIRED_PARTS:
                errors.append(f'{name}/{cid}: retired Rev A part remains selected')
            if isinstance(row.get('qty'), int):
                mpn = row.get('mpn')
                quantities[mpn] = quantities.get(mpn, 0) + row['qty']
    for mpn, expected in REQUIRED_QUANTITIES.items():
        if quantities.get(mpn) != expected:
            errors.append(f'Rev A scope requires {expected} of {mpn}; found {quantities.get(mpn, 0)}')
    print(json.dumps({'scope':'Selection-index structure and block coverage only; not a released BOM, inventory, library or electrical approval',
                      'groups_by_block':counts,'component_groups':len(ids),
                      'unique_order_codes':len(parts),
                      'scope_checks':'Retired power/AO blocks absent; MCU, ADC, four-channel I/O and two isolated buses retained',
                      'failures':errors},indent=2))
    return bool(errors)


if __name__ == '__main__':
    raise SystemExit(main())
