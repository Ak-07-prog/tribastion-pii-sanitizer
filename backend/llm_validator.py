import google.genai as genai
import os
import time
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Use valid public model
model = "models/gemini-2.5-flash"


def get_context(text, value, window=80):
    idx = text.find(value)
    if idx == -1:
        return ""

    start = max(0, idx - window)
    end = min(len(text), idx + len(value) + window)

    return text[start:end].replace("\n", " ")


def llm_validate(text, detected_pii):

    if not detected_pii:
        return detected_pii

    contexts = []

    for p in detected_pii:
        ctx = get_context(text, p["value"])
        contexts.append(f"{p['type']}: {p['value']} | context: {ctx}")

    context_block = "\n".join(contexts)

    prompt = f"""
You are a PII detection validator.

Determine if each detected item belongs to a specific individual.

Items:
{context_block}

Rules:
YES -> personal identifier of an individual
NO -> generic, company, or support contact

Respond EXACTLY in this format:

TYPE: VALUE -> YES or NO
"""

    try:

        # prevent burst rate limits
        time.sleep(0.5)

        response = client.models.generate_content(
            model=model,
            contents=[prompt],
            config={"temperature": 0}
        )

        response_text = response.text

        validated = []

        for pii in detected_pii:

            search = f"{pii['type']}: {pii['value']}"

            if search in response_text:
                part = response_text.split(search)[1][:12]

                if "YES" in part:
                    validated.append(pii)

            else:
                # fallback if model didn't respond exactly
                validated.append(pii)

        return validated

    except Exception as e:
        print(f"LLM validation error: {e}")
        return detected_pii


def generate_attack_narrative(pii_found, attack_vectors):

    if not attack_vectors:
        return "No critical attack vectors detected in this document."

    found_types = [p["type"] for p in pii_found]
    vector_names = [v["attack"] for v in attack_vectors]

    prompt = f"""
You are a cybersecurity analyst.

A document contains these PII types: {found_types}

Possible attack vectors:
{vector_names}

Explain in exactly 3 sentences how an attacker could exploit this data.
Write it as a security warning for an organization.
"""

    try:

        time.sleep(0.5)

        response = client.models.generate_content(
            model=model,
            contents=[prompt],
            config={"temperature": 0.2}
        )

        return response.text

    except Exception as e:
        return f"Attack narrative unavailable: {e}"


# ---- TEST SCRIPT ----
if __name__ == "__main__":

    import sys

    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)

    sys.path.insert(0, parent_dir)

    from backend.detector import combined_detect

    test_text = """
    My name is Rahul Sharma.
    Aadhaar: 5487 8795 5678
    Email: rahul.sharma@gmail.com
    Support: help@company.com
    Phone: +91 9876543210
    """

    print("Step 1 - Raw detections:")

    raw = combined_detect(test_text)

    for r in raw:
        print(f"  {r['type']}: {r['value']}")

    print("\nStep 2 - After LLM validation:")

    validated = llm_validate(test_text, raw)

    for r in validated:
        print(f"  {r['type']}: {r['value']}")

    print("\nExpected: help@company.com should be removed")
