import spacy
import re

patterns = {
    "AADHAAR": r'\b[2-9]{1}[0-9]{3}\s[0-9]{4}\s[0-9]{4}\b',
    "PAN": r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b',
    "EMAIL": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    "PHONE": r'\b(\+91[\-\s]?)?[6-9]\d{9}\b',
    "IP": r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
    "DOB": r'\b(0?[1-9]|[12][0-9]|3[01])[\/\-](0?[1-9]|1[012])[\/\-]\d{4}\b',
    "CARD": r'\b(?:\d{4}[\s\-]?){4}\b',
    "IFSC": r'\b[A-Z]{4}0[A-Z0-9]{6}\b',
    "UPI": r'\b[a-zA-Z0-9.\-_]{2,256}@oksbi|okaxis|okhdfcbank|okicici|ybl|ibl|axl|waicici\b',
    "PASSPORT": r'\b[A-PR-WYa-pr-wy][1-9]\d\s?\d{4}[1-9]\b'
}

nlp = spacy.load("en_core_web_sm")


def regex_detect(text):
    found = []
    for pii_type, pattern in patterns.items():
        matches = re.finditer(pattern, text)
        for match in matches:
            found.append({
                "type": pii_type,
                "value": match.group(),
                "position": match.start(),
                "confidence": 0.95
            })
    return found


def spacy_detect(text):
    doc = nlp(text)
    found = []
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            found.append({
                "type": "NAME",
                "value": ent.text,
                "position": ent.start_char,
                "confidence": 0.85
            })
        elif ent.label_ in ["GPE", "LOC"]:
            found.append({
                "type": "ADDRESS",
                "value": ent.text,
                "position": ent.start_char,
                "confidence": 0.75
            })
    return found


def combined_detect(text):
    regex_results = regex_detect(text)
    spacy_results = spacy_detect(text)
    all_results = regex_results + spacy_results
    seen_positions = set()
    unique_results = []
    for item in all_results:
        if item["position"] not in seen_positions:
            unique_results.append(item)
            seen_positions.add(item["position"])
    return unique_results


if __name__ == "__main__":
    test_text = """
    My name is Rahul Sharma.
    Aadhaar: 5487 8795 5678
    PAN: BGHPM4521K
    Email: rahul.sharma@gmail.com
    Support: help@company.com
    Phone: +91 9876543210
    DOB: 12/05/1978
    IFSC: HDFC0001234
    IP: 103.54.12.77
    I live in Ahmedabad, Gujarat.
    """

    results = combined_detect(test_text)
    print(f"Found {len(results)} PII items:\n")
    for r in results:
        print(f"Type: {r['type']:<12} Value: {r['value']}")
