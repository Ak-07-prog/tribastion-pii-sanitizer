import json
import os
import hashlib
from datetime import datetime

LOG_PATH = "storage/audit_logs/audit.json"

def ensure_log_file():
    os.makedirs("storage/audit_logs", exist_ok=True)
    if not os.path.exists(LOG_PATH):
        with open(LOG_PATH, "w") as f:
            pass

def get_last_hash():
    if not os.path.exists(LOG_PATH):
        return "GENESIS"
    lines = []
    with open(LOG_PATH, "r") as f:
        lines = f.readlines()
    if not lines:
        return "GENESIS"
    try:
        last = json.loads(lines[-1])
        return last.get("entry_hash", "GENESIS")
    except:
        return "GENESIS"

def log(event_data):
    ensure_log_file()
    
    # add timestamp if not present
    if "timestamp" not in event_data:
        event_data["timestamp"] = str(datetime.now())
    
    # tamper evident hash chaining
    last_hash = get_last_hash()
    entry_string = json.dumps(event_data) + last_hash
    entry_hash = hashlib.sha256(entry_string.encode()).hexdigest()[:16]
    event_data["entry_hash"] = entry_hash
    event_data["prev_hash"] = last_hash
    
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(event_data) + "\n")

def log_upload(user, filename, pii_count, risk_score, attack_vectors):
    log({
        "action": "FILE_UPLOAD",
        "user": user,
        "filename": filename,
        "pii_count": pii_count,
        "risk_score": risk_score,
        "attack_vectors": attack_vectors
    })

def log_download(user, filename):
    log({
        "action": "FILE_DOWNLOAD",
        "user": user,
        "filename": filename
    })

def log_login(user, role):
    log({
        "action": "LOGIN",
        "user": user,
        "role": role
    })

def log_logout(user):
    log({
        "action": "LOGOUT",
        "user": user
    })

def log_pii_detection(user, filename, pii_found, risk_score):
    log({
        "action": "PII_DETECTED",
        "user": user,
        "filename": filename,
        "pii_count": len(pii_found),
        "pii_types": list(set([p["type"] for p in pii_found])),
        "risk_score": risk_score
    })

def get_all_logs():
    ensure_log_file()
    logs = []
    with open(LOG_PATH, "r") as f:
        for line in f:
            try:
                logs.append(json.loads(line))
            except:
                pass
    return logs

def verify_chain():
    logs = get_all_logs()
    if not logs:
        return True
    prev_hash = "GENESIS"
    for entry in logs:
        check_data = {k: v for k, v in entry.items()
                      if k not in ["entry_hash", "prev_hash"]}
        check_string = json.dumps(check_data) + prev_hash
        expected_hash = hashlib.sha256(
            check_string.encode()).hexdigest()[:16]
        if entry.get("entry_hash") != expected_hash:
            return False
        prev_hash = entry.get("entry_hash", "")
    return True


# ---- TEST IT ----
if __name__ == "__main__":
    log_login("admin@company.com", "Admin")
    log_upload("admin@company.com", "test.txt", 6, 100, ["SIM Swap"])
    log_pii_detection("admin@company.com", "test.txt",
                      [{"type": "NAME"}, {"type": "AADHAAR"}], 100)
    log_download("user@company.com", "sanitized_test.txt")
    log_logout("admin@company.com")

    logs = get_all_logs()
    print(f"✅ {len(logs)} log entries created")

    chain_valid = verify_chain()
    print(f"✅ Chain integrity: {chain_valid}")

    print("\nLast 3 entries:")
    for entry in logs[-3:]:
        print(f"  {entry['action']} — {entry['user']} — {entry['timestamp'][:19]}")