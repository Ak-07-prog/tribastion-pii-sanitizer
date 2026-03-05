import pandas as pd
import json

def parse_txt(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def parse_csv(filepath):
    df = pd.read_csv(filepath)
    # scan column names themselves
    text = ' '.join(df.columns.tolist())
    # scan all cell values
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


# ---- TEST IT ----
if __name__ == "__main__":
    # test txt
    with open("sample_files/test.txt", "w") as f:
        f.write("My name is Rahul Sharma. Email: rahul@gmail.com")
    print("TXT result:")
    print(parse_txt("sample_files/test.txt"))
    print()

    # test csv
    with open("sample_files/test.csv", "w") as f:
        f.write("name,email,phone\nRahul Sharma,rahul@gmail.com,9876543210")
    print("CSV result:")
    print(parse_csv("sample_files/test.csv"))
    print()

    # test json
    with open("sample_files/test.json", "w") as f:
        json.dump({"name": "Rahul Sharma", "email": "rahul@gmail.com"}, f)
    print("JSON result:")
    print(parse_json("sample_files/test.json"))