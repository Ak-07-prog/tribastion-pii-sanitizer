import re
import hashlib
import random
import string
from faker import Faker

fake = Faker('en_IN')


def apply_masking(value, pii_type, strategy):

    if strategy == "redact":
        return "[REDACTED]"

    elif strategy == "partial":
        if pii_type == "EMAIL":
            parts = value.split("@")
            return parts[0][:2] + "***@" + parts[1]
        elif pii_type == "PHONE":
            return value[:2] + "XXXXXX" + value[-2:]
        elif pii_type == "AADHAAR":
            return "XXXX XXXX " + value[-4:]
        elif pii_type == "PAN":
            return "XXXXX" + value[-4:]
        elif pii_type == "CARD":
            return "XXXX XXXX XXXX " + value[-4:]
        else:
            return value[:2] + "***"

    elif strategy == "pseudonymize":
        if pii_type == "NAME":
            return fake.name()
        elif pii_type == "EMAIL":
            return fake.email()
        elif pii_type == "PHONE":
            return fake.phone_number()
        elif pii_type == "ADDRESS":
            return fake.address()
        else:
            return "[PSEUDONYM]"

    elif strategy == "tokenize":
        token = hashlib.md5(value.encode()).hexdigest()[:8].upper()
        return f"TKN-{pii_type[0]}-{token}"

    elif strategy == "synthetic":
        if pii_type == "AADHAAR":
            return f"{random.randint(2000, 9999)} {random.randint(1000, 9999)} {random.randint(1000, 9999)}"
        elif pii_type == "PAN":
            letters = ''.join(random.choices(string.ascii_uppercase, k=5))
            digits = ''.join(random.choices(string.digits, k=4))
            return letters + digits + random.choice(string.ascii_uppercase)
        elif pii_type == "EMAIL":
            return fake.email()
        elif pii_type == "PHONE":
            return f"+91 {random.randint(6000000000, 9999999999)}"
        else:
            return "[SYNTHETIC]"

    elif strategy == "format_preserving":
        if pii_type == "AADHAAR":
            return f"XXXX XXXX {value[-4:]}"
        elif pii_type == "EMAIL":
            parts = value.split("@")
            return parts[0][:2] + "***@" + parts[1]
        elif pii_type == "PAN":
            return "XXXXX" + value[-4:]
        else:
            return "[MASKED]"

    return "[REDACTED]"


def mask_pii(text, pii_list, strategy):
    # sort by position in reverse so replacements dont shift positions
    pii_sorted = sorted(pii_list, key=lambda x: x["position"], reverse=True)

    for pii in pii_sorted:
        original = pii["value"]
        pii_type = pii["type"]
        masked = apply_masking(original, pii_type, strategy)
        text = text.replace(original, masked)

    return text


# ---- TEST IT ----
if __name__ == "__main__":
    test_text = "Name: Rahul Sharma, Aadhaar: 5487 8795 5678, Email: rahul@gmail.com, PAN: BGHPM4521K"

    pii_list = [
        {"type": "NAME", "value": "Rahul Sharma", "position": 6},
        {"type": "AADHAAR", "value": "5487 8795 5678", "position": 28},
        {"type": "EMAIL", "value": "rahul@gmail.com", "position": 51},
        {"type": "PAN", "value": "BGHPM4521K", "position": 73}
    ]

    strategies = ["redact", "partial", "pseudonymize",
                  "tokenize", "synthetic", "format_preserving"]

    for strategy in strategies:
        result = mask_pii(test_text, pii_list, strategy)
        print(f"{strategy}:")
        print(f"  {result}")
        print()
