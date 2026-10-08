import os, json, time
from datetime import datetime, timezone
from pathlib import Path
import requests

PORTAL = os.getenv('AGOL_PORTAL', 'https://www.arcgis.com').rstrip('/')
LAYER = os.environ['AGOL_LAYER_URL'].rstrip('/')
USER = os.environ['AGOL_USERNAME']
PASSWORD = os.environ['AGOL_PASSWORD']
S = requests.Session()

def post(url, payload):
    r = S.post(url, data=payload, timeout=45)
    r.raise_for_status()
    data = r.json()
    if 'error' in data:
        raise RuntimeError(f"ArcGIS API error: {data['error'].get('message')} {data['error'].get('details')}")
    return data

token = post(f'{PORTAL}/sharing/rest/generateToken', {
    'username': USER, 'password': PASSWORD, 'client': 'referer',
    'referer': PORTAL, 'expiration': 30, 'f': 'json'
})['token']
metadata = post(LAYER, {'f': 'json', 'token': token})
fields = {f['name'].lower(): f['name'] for f in metadata.get('fields', [])}
required = ['objectid', 'nts_id', 'end_dt', 'approval_status']
objectid = metadata.get('objectIdField') or fields.get('objectid')
if not objectid or any(x not in fields for x in required[1:]):
    raise RuntimeError(f'Required fields missing. Available: {sorted(fields.values())}')
selected = [objectid] + [fields[x] for x in required[1:]]
ids_result = post(f'{LAYER}/query', {'where': '1=1', 'returnIdsOnly': 'true', 'f': 'json', 'token': token})
ids = ids_result.get('objectIds') or []
records = []
for i in range(0, len(ids), 100):
    subset = ids[i:i+100]
    result = post(f'{LAYER}/query', {
        'objectIds': ','.join(map(str, subset)), 'outFields': ','.join(selected),
        'returnGeometry': 'false', 'f': 'json', 'token': token
    })
    features = result.get('features', [])
    if len(features) != len(subset):
        raise RuntimeError(f'Incomplete ArcGIS batch: requested {len(subset)}, got {len(features)}')
    for feature in features:
        a = feature['attributes']
        raw_date = a.get(fields['end_dt'])
        if isinstance(raw_date, (int, float)):
            date = datetime.fromtimestamp(raw_date / 1000, timezone.utc).strftime('%Y-%m-%d')
        elif isinstance(raw_date, str):
            date = raw_date[:10]
        else:
            date = None
        records.append({'id': a.get(fields['nts_id']), 'end_dt': date,
                        'approval_status': a.get(fields['approval_status'])})
    time.sleep(0.05)
output = {'updated_at': datetime.now(timezone.utc).isoformat(), 'records': records}
path = Path('data/nts.json')
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'Exported {len(records)} NTS records')
