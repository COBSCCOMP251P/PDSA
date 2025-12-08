"""
Simple Test for Solution Reset System
Assumes server is already running on port 8000
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/eight-queens-game"

print("\n" + "="*70)
print("🧪 Testing Solution Reset System")
print("="*70)

# Test 1: Check Progress
print("\n1️⃣  Checking Current Progress...")
response = requests.get(f"{BASE_URL}/solutions/progress")
if response.status_code == 200:
    data = response.json()
    if data['status'] == 'success':
        progress = data['data']
        print(f"   ✅ Solutions Found: {progress['solutions_found']}/{progress['total_solutions']}")
        print(f"   ✅ Progress: {progress['progress_percentage']}%")
        print(f"   ✅ Remaining: {progress['remaining']}")
    else:
        print(f"   ❌ Error: {data['message']}")
else:
    print(f"   ❌ HTTP Error: {response.status_code}")

# Test 2: Test Manual Reset
print("\n2️⃣  Testing Manual Reset...")
response = requests.post(f"{BASE_URL}/solutions/reset")
if response.status_code == 200:
    data = response.json()
    if data['status'] == 'success':
        print(f"   ✅ Reset successful")
        print(f"   ✅ Message: {data['message']}")
        reset_data = data['data']
        print(f"   ✅ Solutions reset: {reset_data['solutions_reset']}")
        print(f"   ✅ New found count: {reset_data['current_found']}")
    else:
        print(f"   ❌ Error: {data['message']}")
else:
    print(f"   ❌ HTTP Error: {response.status_code}")

# Test 3: Verify reset worked
print("\n3️⃣  Verifying Reset Worked...")
response = requests.get(f"{BASE_URL}/solutions/progress")
if response.status_code == 200:
    data = response.json()
    if data['status'] == 'success':
        progress = data['data']
        print(f"   ✅ Solutions Found: {progress['solutions_found']}/{progress['total_solutions']}")
        if progress['solutions_found'] == 0:
            print(f"   ✅ RESET VERIFIED: All solutions cleared!")
        else:
            print(f"   ⚠️  Warning: {progress['solutions_found']} solutions still marked as found")
    else:
        print(f"   ❌ Error: {data['message']}")
else:
    print(f"   ❌ HTTP Error: {response.status_code}")

# Test 4: Test "Mark All Found" helper
print("\n4️⃣  Testing 'Mark All Found' Helper...")
response = requests.post(f"{BASE_URL}/solutions/test-mark-all-found")
if response.status_code == 200:
    data = response.json()
    if data['status'] == 'success':
        test_data = data['data']
        print(f"   ✅ Marked all solutions as found")
        print(f"   ✅ Solutions marked: {test_data['solutions_marked']}")
        print(f"   ✅ Current found: {test_data['current_found']}")
    else:
        print(f"   ❌ Error: {data['message']}")
else:
    print(f"   ❌ HTTP Error: {response.status_code}")

# Test 5: Verify all marked
print("\n5️⃣  Verifying All Marked...")
response = requests.get(f"{BASE_URL}/solutions/progress")
if response.status_code == 200:
    data = response.json()
    if data['status'] == 'success':
        progress = data['data']
        print(f"   ✅ Solutions Found: {progress['solutions_found']}/{progress['total_solutions']}")
        if progress['solutions_found'] == 92:
            print(f"   ✅ ALL MARKED: Ready for auto-reset test!")
        else:
            print(f"   ⚠️  Warning: Expected 92, got {progress['solutions_found']}")
    else:
        print(f"   ❌ Error: {data['message']}")
else:
    print(f"   ❌ HTTP Error: {response.status_code}")

# Final summary
print("\n" + "="*70)
print("✅ Test Complete!")
print("="*70)
print("\n📝 Next Steps:")
print("   1. Open game at http://127.0.0.1:8000/games/eight_queens/frontend/index.html")
print("   2. Submit any valid solution")
print("   3. Should see 'ALL 92 FOUND!' celebration")
print("   4. Should auto-reset all solutions")
print("   5. Submit same solution again - should now be counted as new")
print("\n" + "="*70)
