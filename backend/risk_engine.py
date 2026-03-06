from datetime import datetime

PII_WEIGHTS = {
    "AADHAAR": 10,
    "PAN": 9,
    "CARD": 10,
    "PASSPORT": 9,
    "PHONE": 6,
    "EMAIL": 5,
    "NAME": 4,
    "ADDRESS": 5,
    "DOB": 7,
    "IFSC": 8,
    "UPI": 7,
    "IP": 4
}

ATTACK_VECTORS = [
    {
        "combination": ["AADHAAR", "DOB", "NAME"],
        "attack": "SIM Swap Attack",
        "severity": "CRITICAL",
        "description": "Attacker can contact telecom provider and take over victim's phone number bypassing 2FA"
    },
    {
        "combination": ["PAN", "CARD", "IFSC"],
        "attack": "Financial Fraud",
        "severity": "CRITICAL",
        "description": "Attacker can initiate unauthorized bank transfers and credit card fraud"
    },
    {
        "combination": ["EMAIL", "PHONE", "ADDRESS"],
        "attack": "Phishing + Physical Stalking",
        "severity": "HIGH",
        "description": "Attacker can conduct targeted phishing and locate victim physically"
    },
    {
        "combination": ["EMAIL", "NAME"],
        "attack": "Spear Phishing",
        "severity": "MEDIUM",
        "description": "Attacker can send highly personalized phishing emails"
    },
    {
        "combination": ["AADHAAR", "PAN"],
        "attack": "Identity Theft",
        "severity": "CRITICAL",
        "description": "Complete identity can be stolen for financial and legal fraud"
    },
    {
        "combination": ["CARD", "DOB"],
        "attack": "Credit Card Fraud",
        "severity": "CRITICAL",
        "description": "Attacker can bypass card verification using DOB as security answer"
    },
    {
        "combination": ["EMAIL", "PHONE"],
        "attack": "Account Takeover",
        "severity": "HIGH",
        "description": "Attacker can reset passwords and take over online accounts"
    },
    {
        "combination": ["NAME", "ADDRESS", "PHONE"],
        "attack": "Social Engineering Attack",
        "severity": "HIGH",
        "description": "Attacker can impersonate victim or conduct targeted scams"
    }
]

COMPLIANCE_MAP = {
    "AADHAAR": "UIDAI Data Protection Guidelines Violated",
    "PAN": "Income Tax Act Privacy Requirements Violated",
    "CARD": "PCI-DSS Compliance Violated",
    "PASSPORT": "Passport Act Privacy Requirements Violated",
    "IFSC": "RBI Data Security Guidelines Violated"
}


def calculate_risk(pii_found):
    if not pii_found:
        return {
            "score": 0,
            "level": "LOW",
            "attack_vectors": [],
            "vector_details": [],
            "compliance_flags": []
        }

    found_types = list(set([p["type"] for p in pii_found]))

    # calculate base score
    raw_score = sum([PII_WEIGHTS.get(t, 3) for t in found_types])
    normalized_score = min(100, raw_score * 4)

    # detect attack vectors
    detected_vectors = []
    for vector in ATTACK_VECTORS:
        if all(c in found_types for c in vector["combination"]):
            detected_vectors.append(vector)

    # boost score if critical combinations found
    if any(v["severity"] == "CRITICAL" for v in detected_vectors):
        normalized_score = max(normalized_score, 85)
    elif any(v["severity"] == "HIGH" for v in detected_vectors):
        normalized_score = max(normalized_score, 65)

    # determine level
    if normalized_score >= 80:
        level = "CRITICAL"
    elif normalized_score >= 60:
        level = "HIGH"
    elif normalized_score >= 40:
        level = "MEDIUM"
    else:
        level = "LOW"

    # compliance flags
    compliance_flags = []
    for pii_type in found_types:
        if pii_type in COMPLIANCE_MAP:
            compliance_flags.append(COMPLIANCE_MAP[pii_type])

    return {
        "score": normalized_score,
        "level": level,
        "attack_vectors": [v["attack"] for v in detected_vectors],
        "vector_details": detected_vectors,
        "compliance_flags": list(set(compliance_flags))
    }


# ---- TEST IT ----
if __name__ == "__main__":
    # simulate detected PII
    test_pii = [
        {"type": "NAME", "value": "Rahul Sharma",
            "position": 0, "confidence": 0.95},
        {"type": "AADHAAR", "value": "5487 8795 5678",
            "position": 10, "confidence": 0.99},
        {"type": "DOB", "value": "12/05/1978", "position": 20, "confidence": 0.95},
        {"type": "EMAIL", "value": "rahul@gmail.com",
            "position": 30, "confidence": 0.98},
        {"type": "PAN", "value": "BGHPM4521K", "position": 40, "confidence": 0.99},
        {"type": "PHONE", "value": "9876543210",
            "position": 50, "confidence": 0.97}
    ]

    result = calculate_risk(test_pii)

    print(f"Risk Score: {result['score']}/100")
    print(f"Risk Level: {result['level']}")
    print(f"\nAttack Vectors Detected:")
    for vector in result['vector_details']:
        print(f"  🔴 {vector['attack']} ({vector['severity']})")
        print(f"     {vector['description']}")
    print(f"\nCompliance Flags:")
    for flag in result['compliance_flags']:
        print(f"  🚨 {flag}")
