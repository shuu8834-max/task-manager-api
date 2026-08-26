import json
import urllib.request

print("🔐 Starting Secure API Authentication Testing...")
# FIX: Using localhost routes the security data internally without Windows network blockages
base_url = "http://localhost:8080/api"

# 1. Register a professional developer profile
reg_data = json.dumps({"username": "alex", "password": "secure123"}).encode(
    "utf-8"
)
req_reg = urllib.request.Request(
    f"{base_url}/register",
    data=reg_data,
    headers={"Content-Type": "application/json"},
    method="POST",
)

try:
    with urllib.request.urlopen(req_reg) as response:
        print("✅ step 1: Registration Success!")
except Exception as e:
    print(f"⚠️ Registration Info: {e} (Account may already exist)")

# 2. Login to extract the cryptographic JWT Token
login_data = json.dumps({"username": "alex", "password": "secure123"}).encode(
    "utf-8"
)
req_log = urllib.request.Request(
    f"{base_url}/login",
    data=login_data,
    headers={"Content-Type": "application/json"},
    method="POST",
)

token = None
try:
    with urllib.request.urlopen(req_log) as response:
        res = json.loads(response.read().decode("utf-8"))
        token = res["token"]
        print("✅ step 2: Login Success! Token secured.")
except Exception as e:
    print(f"❌ Login Failed: {e}")

# 3. Use token payload to insert data into a private account container
if token:
    task_data = json.dumps(
        {"title": "Review JWT Authentication logic"}
    ).encode("utf-8")
    req_task = urllib.request.Request(
        f"{base_url}/tasks",
        data=task_data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",  # Attaching security credential
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req_task) as response:
            print("✅ step 3: Secure Task Insertion Approved!")
    except Exception as e:
        print(f"❌ Token Injection Failed: {e}")

