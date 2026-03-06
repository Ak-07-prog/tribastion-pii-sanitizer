import pandas as pd
import json
import re
import fitz
import sqlparse
import xml.etree.ElementTree as ET
from docx import Document


def parse_txt(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def parse_csv(filepath):
    df = pd.read_csv(filepath)
    text = ' '.join(df.columns.tolist())
    text += ' ' + df.to_string()
    return text


def parse_json(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)

    def extract_values(obj):
        if isinstance(obj, dict):
            return ' '.join([extract_values(v) for v in obj.values()])
        elif isinstance(obj, list):
            return ' '.join([extract_values(i) for i in obj])
        else:
            return str(obj)

    return extract_values(data)


def parse_pdf(filepath):
    text = ""
    doc = fitz.open(filepath)
    for page in doc:
        text += page.get_text()
    doc.close()
    return text


def parse_docx(filepath):
    doc = Document(filepath)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                text += cell.text + " "
    return text


def parse_sql(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    values = re.findall(r"'([^']*)'", content)
    return ' '.join(values) + ' ' + content


def parse_xml(filepath):
    tree = ET.parse(filepath)
    root = tree.getroot()

    def extract_xml(element):
        text = element.tag + " "
        if element.text and element.text.strip():
            text += element.text.strip() + " "
        for attr_name, attr_value in element.attrib.items():
            text += attr_name + " " + attr_value + " "
        for child in element:
            text += extract_xml(child)
        return text

    return extract_xml(root)


def extract_text(filepath):
    ext = filepath.split(".")[-1].lower()

    if ext == "txt":
        return parse_txt(filepath)
    elif ext == "csv":
        return parse_csv(filepath)
    elif ext == "json":
        return parse_json(filepath)
    elif ext == "pdf":
        return parse_pdf(filepath)
    elif ext == "docx":
        return parse_docx(filepath)
    elif ext == "sql":
        return parse_sql(filepath)
    elif ext == "xml":
        return parse_xml(filepath)
    else:
        try:
            return parse_txt(filepath)
        except:
            return ""


# ---- TEST IT ----
if __name__ == "__main__":
    print("TXT:"); print(parse_txt("sample_files/test.txt")); print()
    print("CSV:"); print(parse_csv("sample_files/test.csv")); print()
    print("JSON:"); print(parse_json("sample_files/test.json")); print()
    print("PDF:"); print(parse_pdf("sample_files/test.pdf")); print()
    print("DOCX:"); print(parse_docx("sample_files/test.docx")); print()
    print("SQL:"); print(parse_sql("sample_files/test.sql")); print()
    print("XML:"); print(parse_xml("sample_files/test.xml")); print()
    print("✅ All parsers working")