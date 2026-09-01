import json
from urllib import request as urllib_request

base = 'http://127.0.0.1:8000/api/v1'

def post(path, payload, headers=None):
    data = json.dumps(payload).encode()
    req = urllib_request.Request(base + path, data=data, headers={**(headers or {}), 'Content-Type': 'application/json'})
    try:
        with urllib_request.urlopen(req) as r:
            return r.status, json.loads(r.read())
    except urllib_request.HTTPError as e:
        return e.code, e.read().decode()

def get(path, headers=None):
    req = urllib_request.Request(base + path, headers=headers or {})
    try:
        with urllib_request.urlopen(req) as r:
            return r.status, json.loads(r.read())
    except urllib_request.HTTPError as e:
        return e.code, e.read().decode()

login_status, login_body = post('/auth/login', {'email': 'admin@familia.com', 'password': 'familia123'})
token = login_body['access_token']
headers = {'Authorization': f'Bearer {token}'}

events_status, events_body = get('/events?year=2026&month=8', headers)
print('events', events_status, len(events_body), 'items')
print(json.dumps(events_body[:5], ensure_ascii=False, indent=2))

prep_status, prep_body = get('/month/prepare', headers)
print('prepare', prep_status, prep_body)
