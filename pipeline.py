# pipeline.py
# THIS IS THE CONTRACT — NEVER CHANGE KEY NAMES AFTER THIS POINT
# Member 1 fills in the real logic later
# Member 3 only ever calls process_file() and nothing else

from datetime import datetime


def process_file(filepath, masking_strategy):
    """
    filepath: string — path to uploaded file
    masking_strategy: string — one of:
        "redact", "partial", "pseudonymize", 
        "tokenize", "synthetic", "format_preserving"

    ALWAYS returns exactly these keys — never add or remove keys
    """
    return {
        "sanitized_text": "",       # string
        "pii_found": [],            # list of dicts
        "risk_score": 0,            # integer 0-100
        "risk_level": "",           # "LOW/MEDIUM/HIGH/CRITICAL"
        "attack_vectors": [],       # list of strings
        "attack_narrative": "",     # string paragraph
        "compliance_flags": [],     # list of strings
        "sanitized_image": None,    # image path or None
        "audit_data": {}            # dict
    }


def save_file(filepath):
    """
    filepath: string — path to file to save
    returns: string — unique file ID
    """
    return ""


def log_event(event_data):
    """
    event_data: dict — contains action, user, timestamp etc
    returns: nothing
    """
    pass
