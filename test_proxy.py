import urllib.request
import urllib.parse
import json

data = {
    'method': 'GET',
    'url': 'http://map.geoshare.com.cn:9080/kpi/devQualityDefect/page?page=1&pageSize=1&projectId=2029759625003290625&orderByField=updateTime&orderBy=desc',
    'headers': {
        'accept': 'application/json, text/plain, */*',
        'authorization': 'Bearer eyJhbGciOiJIUzUxMiJ9.eyJ1c2VyX2lkIjoyMDI5NzUwOTM2NDIyODU0NjU3LCJ1c2VyX2tleSI6IjMwYjQ1MzU1LWVkZDItNDMxMi1hZjY0LTBiY2E0ZTllODYzNCIsInVzZXJuYW1lIjoi5bSU5a2Q6L2pIn0.z2gyTnL6etQx1tFLp9aLvYbcGZklFVjLgZ-2c-XimGG3zqv9_urBhIwl6N1fEX_vbKl8b_VytvPNxSAK6CB5vA'
    },
    'params': {}
}

print("Sending request to proxy...")

req = urllib.request.Request(
    'http://localhost:8000/proxy/',
    data=json.dumps(data).encode('utf-8'),
    headers={'Content-Type': 'application/json'},
    method='POST'
)

try:
    with urllib.request.urlopen(req, timeout=30) as response:
        resp_json = json.loads(response.read().decode('utf-8'))
        print(f"Success: {resp_json.get('success')}")
        print(f"Status code: {resp_json.get('status_code')}")
        content = resp_json.get('content', '')
        print(f"Content (first 1000 chars): {content[:1000]}")
except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code}")
    print(e.read().decode('utf-8')[:1000])
except Exception as e:
    print(f"Error: {e}")
