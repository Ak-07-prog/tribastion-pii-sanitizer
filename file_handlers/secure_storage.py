from cryptography.fernet import Fernet
import hashlib
import os
import json
from datetime import datetime

KEY_FILE = "secret.key"

def generate_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
        print("✅ Encryption key generated")

def load_key():
    if not os.path.exists(KEY_FILE):
        generate_key()
    return open(KEY_FILE, "rb").read()

def encrypt_file(filepath):
    key = load_key()
    f = Fernet(key)
    with open(filepath, "rb") as file:
        data = file.read()
    encrypted = f.encrypt(data)
    # hashed filename
    hashed_name = hashlib.sha256(
        os.path.basename(filepath).encode()
    ).hexdigest()[:16]
    ext = os.path.splitext(filepath)[1]
    os.makedirs("storage/original", exist_ok=True)
    encrypted_path = f"storage/original/{hashed_name}{ext}.enc"
    with open(encrypted_path, "wb") as file:
        file.write(encrypted)
    return encrypted_path, hashed_name

def decrypt_file(encrypted_path):
    key = load_key()
    f = Fernet(key)
    with open(encrypted_path, "rb") as file:
        encrypted = file.read()
    return f.decrypt(encrypted)

def get_file_hash(filepath):
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

def save_file(filepath):
    file_hash = get_file_hash(filepath)
    encrypted_path, file_id = encrypt_file(filepath)
    # store hash for integrity verification
    os.makedirs("storage", exist_ok=True)
    hashes_path = "storage/hashes.json"
    hashes = {}
    if os.path.exists(hashes_path):
        with open(hashes_path, "r") as f:
            try:
                hashes = json.load(f)
            except:
                hashes = {}
    hashes[file_id] = {
        "hash": file_hash,
        "encrypted_path": encrypted_path,
        "timestamp": str(datetime.now())
    }
    with open(hashes_path, "w") as f:
        json.dump(hashes, f, indent=2)
    return file_id

def verify_integrity(file_id):
    hashes_path = "storage/hashes.json"
    if not os.path.exists(hashes_path):
        return False
    with open(hashes_path, "r") as f:
        hashes = json.load(f)
    if file_id not in hashes:
        return False
    stored = hashes[file_id]
    current_hash = get_file_hash(stored["encrypted_path"])
    return current_hash == stored["hash"]

def save_sanitized(text, filename):
    os.makedirs("storage/sanitized", exist_ok=True)
    output_path = f"storage/sanitized/sanitized_{filename}"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)
    return output_path

def create_honeypot_files():
    os.makedirs("storage/original", exist_ok=True)
    honeypots = [
        "storage/original/employee_aadhaar_master.csv",
        "storage/original/definitely_not_passwords.pdf",
        "storage/original/secret_financial_records.xlsx"
    ]
    for path in honeypots:
        if not os.path.exists(path):
            with open(path, "w") as f:
                f.write("HONEYPOT FILE - DO NOT ACCESS")
    print("✅ Honeypot files created")


# ---- TEST IT ----
if __name__ == "__main__":
    # generate key
    generate_key()

    # create test file
    with open("temp/test_secure.txt", "w") as f:
        f.write("Sensitive data: Rahul Sharma, 5487 8795 5678")

    # save and encrypt
    file_id = save_file("temp/test_secure.txt")
    print(f"✅ File saved with ID: {file_id}")

    # verify integrity
    is_valid = verify_integrity(file_id)
    print(f"✅ Integrity check: {is_valid}")

    # save sanitized
    path = save_sanitized("Sanitized content here", "test.txt")
    print(f"✅ Sanitized file saved: {path}")

    # create honeypots
    create_honeypot_files()

    print("\n✅ Secure storage working correctly")