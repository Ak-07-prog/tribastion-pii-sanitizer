import easyocr
import cv2
import numpy as np
from PIL import Image
import os

reader = easyocr.Reader(['en'])

def process_image(filepath):
    # extract text via OCR
    results = reader.readtext(filepath)
    extracted_text = ' '.join([res[1] for res in results])
    text_regions = [{"bbox": res[0], "text": res[1]} for res in results]

    # detect ID card type
    id_type = detect_id_type(extracted_text)

    # load image for visual processing
    image = cv2.imread(filepath)

    # blur faces
    image = blur_faces(image)

    return {
        "extracted_text": extracted_text,
        "text_regions": text_regions,
        "id_type": id_type,
        "image": image
    }


def detect_id_type(text):
    text_upper = text.upper()
    if "AADHAAR" in text_upper or "UIDAI" in text_upper:
        return "AADHAAR"
    elif "INCOME TAX" in text_upper or "PAN" in text_upper:
        return "PAN"
    elif "PASSPORT" in text_upper:
        return "PASSPORT"
    elif "DRIVING" in text_upper or "LICENCE" in text_upper:
        return "DRIVING_LICENSE"
    return "UNKNOWN"


def blur_faces(image):
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    )
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    for (x, y, w, h) in faces:
        face_region = image[y:y+h, x:x+w]
        blurred = cv2.GaussianBlur(face_region, (99, 99), 30)
        image[y:y+h, x:x+w] = blurred
    return image


def redact_pii_regions(image, text_regions, pii_values):
    for region in text_regions:
        for pii in pii_values:
            if pii.lower() in region["text"].lower():
                bbox = region["bbox"]
                pts = np.array(bbox, np.int32)
                cv2.fillPoly(image, [pts], (0, 0, 0))
    return image


def strip_exif(filepath, output_path):
    image = Image.open(filepath)
    data = list(image.getdata())
    clean_image = Image.new(image.mode, image.size)
    clean_image.putdata(data)
    clean_image.save(output_path)


def save_processed_image(image, output_path):
    cv2.imwrite(output_path, image)
    return output_path


# ---- TEST IT ----
if __name__ == "__main__":
    # create a simple test image with text
    test_image = np.ones((200, 600, 3), dtype=np.uint8) * 255
    cv2.putText(test_image, "Name: Rahul Sharma", (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    cv2.putText(test_image, "Aadhaar: 5487 8795 5678", (10, 100),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    cv2.putText(test_image, "Email: rahul@gmail.com", (10, 150),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    cv2.imwrite("sample_files/test_image.png", test_image)
    print("✅ Test image created")

    print("Running OCR...")
    result = process_image("sample_files/test_image.png")
    print(f"Extracted text: {result['extracted_text']}")
    print(f"ID type: {result['id_type']}")
    print(f"Text regions found: {len(result['text_regions'])}")
    print("✅ Image processor working")