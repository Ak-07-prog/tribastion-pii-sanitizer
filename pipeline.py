from file_handlers.parser import extract_text
from backend.risk_engine import calculate_risk
from backend.masker import mask_pii
from backend.llm_validator import llm_validate, generate_attack_narrative
from backend.detector import combined_detect
from datetime import datetime
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def process_file(filepath, masking_strategy):
    try:
        # step 1 — extract text based on file type
        ext = filepath.split(".")[-1].lower()

        if ext in ["png", "jpg", "jpeg"]:
            # image file — use OCR
            from file_handlers.image_processor import process_image
            image_result = process_image(filepath)
            text = image_result["extracted_text"]
        else:
            text = extract_text(filepath)

        if not text or text.strip() == "":
            return _empty_result()

        # step 2 — detect PII
        raw_detections = combined_detect(text)

        # step 3 — validate with LLM
        try:
            validated_detections = llm_validate(text, raw_detections)
        except:
            validated_detections = raw_detections

        # step 4 — mask PII
        sanitized_text = mask_pii(text, validated_detections, masking_strategy)

        # step 5 — calculate risk
        risk_data = calculate_risk(validated_detections)

        # step 6 — generate attack narrative
        try:
            narrative = generate_attack_narrative(
                validated_detections,
                risk_data["vector_details"]
            )
        except:
            narrative = "Attack narrative unavailable."

        result = {
            "sanitized_text": sanitized_text,
            "pii_found": validated_detections,
            "risk_score": risk_data["score"],
            "risk_level": risk_data["level"],
            "attack_vectors": risk_data["attack_vectors"],
            "attack_narrative": narrative,
            "compliance_flags": risk_data["compliance_flags"],
            "sanitized_image": None,
            "audit_data": {
                "timestamp": str(datetime.now()),
                "pii_count": len(validated_detections),
                "processing_time": "calculated"
            }
        }

        # log the processing event
        try:
            from file_handlers.audit_logger import log_upload, log_pii_detection
            user = "system"
            filename = os.path.basename(filepath)
            log_upload(user, filename,
                       len(validated_detections),
                       risk_data["score"],
                       risk_data["attack_vectors"])
            log_pii_detection(user, filename,
                              validated_detections,
                              risk_data["score"])
        except Exception as e:
            print(f"Logging error: {e}")

        return result

    except Exception as e:
        print(f"Pipeline error: {e}")
        return _empty_result()


def _empty_result():
    return {
        "sanitized_text": "",
        "pii_found": [],
        "risk_score": 0,
        "risk_level": "LOW",
        "attack_vectors": [],
        "attack_narrative": "No PII detected.",
        "compliance_flags": [],
        "sanitized_image": None,
        "audit_data": {}
    }


def save_file(filepath):
    try:
        from file_handlers.secure_storage import save_file as _save
        return _save(filepath)
    except Exception as e:
        print(f"Save error: {e}")
        return "file_id_error"


def log_event(event_data):
    try:
        from file_handlers.audit_logger import log
        log(event_data)
    except Exception as e:
        print(f"Log error: {e}")


# ---- TEST IT ----
if __name__ == "__main__":
    # create test file
    with open("sample_files/test.txt", "w") as f:
        f.write("""
        Employee Report
        Name: Rahul Sharma
        Aadhaar: 5487 8795 5678
        Email: rahul.sharma@gmail.com
        Support: help@company.com
        Phone: +91 9876543210
        PAN: BGHPM4521K
        DOB: 12/05/1978
        """)

    print("Testing real pipeline...")
    result = process_file("sample_files/test.txt", "redact")

    print(f"\nSanitized text:")
    print(result["sanitized_text"])
    print(f"\nPII found: {len(result['pii_found'])} items")
    print(f"Risk Score: {result['risk_score']}/100")
    print(f"Risk Level: {result['risk_level']}")
    print(f"Attack Vectors: {result['attack_vectors']}")
    print(f"Compliance: {result['compliance_flags']}")
