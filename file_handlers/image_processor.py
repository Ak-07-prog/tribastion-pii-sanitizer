import easyocr
import cv2
import numpy as np
from PIL import Image
import os
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

reader = easyocr.Reader(['en'], gpu=False)


def preprocess_image(filepath):
    image = cv2.imread(filepath)
    # resize if too small
    h, w = image.shape[:2]
    if w < 800:
        scale = 800 / w
        image = cv2.resize(image, None, fx=scale, fy=scale)
    # convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # increase contrast
    gray = cv2.equalizeHist(gray)
    # denoise
    gray = cv2.fastNlMeansDenoising(gray, h=10)
    # threshold
    _, thresh = cv2.threshold(
        gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return image, thresh


def process_image(filepath):
    image, preprocessed = preprocess_image(filepath)

    # run OCR on preprocessed image
    results = reader.readtext(preprocessed)

    # if low confidence try original
    if not results or all(r[2] < 0.3 for r in results):
        results = reader.readtext(filepath)

    extracted_text = ' '.join([res[1] for res in results])
    text_regions = [{"bbox": res[0], "text": res[1],
                     "confidence": res[2]} for res in results]

    id_type = detect_id_type(extracted_text)
    image_color = cv2.imread(filepath)
    image_color = blur_faces(image_color)

    return {
        "extracted_text": extracted_text,
        "text_regions": text_regions,
        "id_type": id_type,
        "image": image_color
    }


def detect_id_type(text):
    text_upper = text.upper()
    if "AADHAAR" in text_upper or "UIDAI" in text_upper or "UNIQUE IDENTIFICATION" in text_upper:
        return "AADHAAR"
    elif "INCOME TAX" in text_upper or "PERMANENT ACCOUNT" in text_upper:
        return "PAN"
    elif "PASSPORT" in text_upper or "REPUBLIC OF INDIA" in text_upper:
        return "PASSPORT"
    elif "DRIVING" in text_upper or "LICENCE" in text_upper:
        return "DRIVING_LICENSE"
    # check for Aadhaar number pattern
    import re
    if re.search(r'\b[2-9]\d{3}\s\d{4}\s\d{4}\b', text):
        return "AADHAAR"
    if re.search(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b', text):
        return "PAN"
    return "UNKNOWN"


def blur_faces(image):
    try:
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        for (x, y, w, h) in faces:
            face_region = image[y:y+h, x:x+w]
            blurred = cv2.GaussianBlur(face_region, (99, 99), 30)
            image[y:y+h, x:x+w] = blurred
    except:
        pass
    return image


def redact_pii_regions(image, text_regions, pii_values):
    import re
    redacted = image.copy()
    h, w = redacted.shape[:2]

    for region in text_regions:
        bbox = region["bbox"]
        region_text = region["text"].strip()

        if not region_text:
            continue

        # check if this region is a pure label (ends with colon or is a known header)
        is_label = bool(re.search(r':\s*$', region_text))
        is_header = bool(re.search(
            r'government|india|income tax|department|aadhaar|union bank|passbook|permanent account|MALE|FEMALE',
            region_text, re.IGNORECASE
        ))

        if is_label or is_header:
            continue

        # check if it matches any detected PII value
        matched_pii = any(
            len(pii) > 2 and (
                pii.lower() in region_text.lower() or
                region_text.lower() in pii.lower()
            )
            for pii in pii_values
        )

        # also redact if it looks like a value (number, name-like, address)
        looks_like_value = bool(re.search(
            r'\d{4,}|^[A-Z][a-z]+(\s[A-Z][a-z]+)*$|S\/O|AT\s*[-–]|PO\+|DIST',
            region_text
        ))

        if matched_pii or looks_like_value:
            pts = np.array(bbox, np.int32)
            cv2.fillPoly(redacted, [pts], (0, 0, 0))

    return redacted


def strip_exif(filepath, output_path):
    image = Image.open(filepath)
    data = list(image.getdata())
    clean_image = Image.new(image.mode, image.size)
    clean_image.putdata(data)
    clean_image.save(output_path)


def save_processed_image(image, output_path):
    cv2.imwrite(output_path, image)
    return output_path
