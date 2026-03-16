from ml_model.layoutlm_extractor import ml_extract_fields
from ocr_extractor import extract_invoice_data_ocr

def extract_invoice_data(file_path):
    try:
        data, confidence = ml_extract_fields(file_path)
        if confidence.get("invoice_number",0) < 70:
            print("Low ML confidence. Using OCR fallback...")
            data = extract_invoice_data_ocr(file_path)
            confidence = {k: 100 if data[k] != "Not Found" else 0 for k in data}
        return {**data, "confidence": confidence}
    except Exception as e:
        print("ML extraction failed:", e)
        data = extract_invoice_data_ocr(file_path)
        confidence = {k: 100 if data[k] != "Not Found" else 0 for k in data}
        return {**data, "confidence": confidence}