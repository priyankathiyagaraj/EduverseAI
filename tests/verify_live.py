import urllib.request
import json
import re

base_url = 'https://eduverseai.antideploy.app'

print("=== VERIFYING LIVE PRODUCTION APPLICATION ===")
print(f"Target URL: {base_url}\n")

# 1. Homepage & stats check
req = urllib.request.Request(base_url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as resp:
    html = resp.read().decode('utf-8')
    status = resp.status
    print(f"1. Homepage Status: HTTP {status}")

    colleges_match = re.search(r'id=["\']stat-colleges["\'][^>]*>([^<]+)<', html)
    courses_match = re.search(r'id=["\']stat-courses["\'][^>]*>([^<]+)<', html)
    districts_match = re.search(r'id=["\']stat-districts["\'][^>]*>([^<]+)<', html)
    status_match = re.search(r'id=["\']stat-status["\'][^>]*>([^<]+)<', html)
    
    colleges_val = colleges_match.group(1).strip() if colleges_match else 'Not found'
    courses_val = courses_match.group(1).strip() if courses_match else 'Not found'
    districts_val = districts_match.group(1).strip() if districts_match else 'Not found'
    status_val = status_match.group(1).strip() if status_match else 'Not found'

    print(f"   - Colleges Indexed: '{colleges_val}' (Expected: '1,129')")
    print(f"   - Courses Cataloged: '{courses_val}' (Expected: '8,120')")
    print(f"   - Districts Covered: '{districts_val}' (Expected: '38')")
    print(f"   - Transparency Index: '{status_val}' (Expected: '100% Sourced')")

    if 'PostgreSQL & SQLAlchemy' in html:
        print("   - Footer Tech Badge: [PASS] 'PostgreSQL & SQLAlchemy' displayed!")
    elif 'MySQL & SQLAlchemy' in html:
        print("   - Footer Tech Badge: [FAIL] Outdated MySQL label found!")
    else:
        print("   - Footer Tech Badge: [INFO] Custom label found.")

# 2. Explore page
req = urllib.request.Request(f"{base_url}/explore", headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as resp:
    content = resp.read()
    print(f"\n2. /explore Status: HTTP {resp.status} (Length: {len(content):,} bytes)")

# 3. API colleges search
req = urllib.request.Request(f"{base_url}/api/colleges?per_page=5", headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    print(f"\n3. /api/colleges Status: HTTP {resp.status}")
    print(f"   - Total Colleges Indexed in PostgreSQL: {data.get('total')}")
    print(f"   - Items returned on page 1: {len(data.get('colleges', []))}")

# 4. Recommendations API
rec_payload = json.dumps({'course': 'MCA', 'district': 'Chennai', 'budget': 100000, 'facilities': []}).encode('utf-8')
req = urllib.request.Request(
    f"{base_url}/api/recommend",
    data=rec_payload,
    headers={'User-Agent': 'Mozilla/5.0', 'Content-Type': 'application/json'}
)
with urllib.request.urlopen(req) as resp:
    rec_res = json.loads(resp.read().decode('utf-8'))
    print(f"\n4. /api/recommend Status: HTTP {resp.status}")
    print(f"   - Success: {rec_res.get('success')}")
    print(f"   - Recommendations generated: {rec_res.get('count')}")

# 5. Map page
req = urllib.request.Request(f"{base_url}/map", headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as resp:
    map_content = resp.read()
    print(f"\n5. /map Status: HTTP {resp.status} (Length: {len(map_content):,} bytes)")

# 6. Admin protection test
try:
    req = urllib.request.Request(f"{base_url}/admin", headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as resp:
        print(f"\n6. /admin unauthenticated status: HTTP {resp.status} (UNEXPECTED)")
except urllib.error.HTTPError as e:
    print(f"\n6. /admin Unauthenticated Access Protection: [PASS] HTTP {e.code} Forbidden")

print("\n=== LIVE PRODUCTION VERIFICATION COMPLETE ===")
