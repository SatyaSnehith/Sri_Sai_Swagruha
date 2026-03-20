"""
Concurrent user test: 10-20 users each add random items to cart and proceed to booking.
Run the Flask app first:  python app.py
Then run this:            python test_concurrent_users.py
"""

import threading
import random
import io
import time
import requests

BASE_URL = "http://127.0.0.1:5000"

PRODUCTS = [
    "Garelu (Pappu)",
    "Garelu (Palli)",
    "Murukulu (Regular)",
    "Murukulu (Broad)",
    "Arisalu",
    "Karjikayalu",
    "Sunnundalu",
    "Boondhi Laddu",
    "Ravva Laddu",
    "Palli Laddu",
    "Sakinalu (Salted)",
    "Sakinalu (Karam)",
    "Gavvalu",
    "salividi",
    "chuduva",
]

results = []
results_lock = threading.Lock()


def simulate_user(user_id):
    session = requests.Session()
    log = []

    try:
        # Step 1: Visit home
        r = session.get(f"{BASE_URL}/", timeout=10)
        log.append(f"  GET /          → {r.status_code}")

        # Step 2: Visit menu
        r = session.get(f"{BASE_URL}/menu", timeout=10)
        log.append(f"  GET /menu      → {r.status_code}")

        # Step 3: Add 1–3 random items
        items_to_add = random.sample(PRODUCTS, k=random.randint(1, 3))
        for item in items_to_add:
            qty = random.randint(1, 5)
            r = session.post(
                f"{BASE_URL}/add",
                data={"item": item, "qty": qty},
                allow_redirects=True,
                timeout=10,
            )
            log.append(f"  POST /add ({item[:20]:<20} x{qty}) → {r.status_code}")

        # Step 4: View cart
        r = session.get(f"{BASE_URL}/cart", timeout=10)
        log.append(f"  GET /cart      → {r.status_code}")

        # Step 5: GET booking page
        r = session.get(f"{BASE_URL}/booking", timeout=10)
        log.append(f"  GET /booking   → {r.status_code}")

        # Step 6: POST booking with a dummy payment slip
        fake_slip = io.BytesIO(b"fake payment slip content")
        r = session.post(
            f"{BASE_URL}/booking",
            data={
                "name": f"Test User {user_id}",
                "phone": f"90000{user_id:05d}",
            },
            files={"slip": ("slip.txt", fake_slip, "text/plain")},
            allow_redirects=False,  # don't follow the WhatsApp redirect
            timeout=10,
        )
        log.append(f"  POST /booking  → {r.status_code} (redirect: {r.headers.get('Location', '')[:60]})")
        success = r.status_code in (302, 200)

    except Exception as e:
        log.append(f"  ERROR: {e}")
        success = False

    with results_lock:
        results.append({"user_id": user_id, "success": success, "log": log})


def run(num_users=15):
    print(f"\nLaunching {num_users} concurrent users against {BASE_URL}\n")

    # Quick connectivity check
    try:
        requests.get(BASE_URL, timeout=5)
    except Exception:
        print("ERROR: Flask app is not running. Start it with:  python app.py\n")
        return

    threads = [threading.Thread(target=simulate_user, args=(i,)) for i in range(1, num_users + 1)]

    start = time.time()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    elapsed = time.time() - start

    # Report
    print(f"{'='*60}")
    for r in sorted(results, key=lambda x: x["user_id"]):
        status = "PASS" if r["success"] else "FAIL"
        print(f"User {r['user_id']:>2}  [{status}]")
        for line in r["log"]:
            print(line)
        print()

    passed = sum(1 for r in results if r["success"])
    print(f"{'='*60}")
    print(f"Results: {passed}/{num_users} passed  |  Total time: {elapsed:.2f}s")


if __name__ == "__main__":
    import sys
    num_users = int(sys.argv[1]) if len(sys.argv) > 1 else 15
    run(num_users)
