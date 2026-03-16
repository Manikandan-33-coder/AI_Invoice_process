import re
from pdf2image import convert_from_path
import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_invoice_data_ocr(file_path):
    text = ""
    images = convert_from_path(file_path, dpi=300) if file_path.lower().endswith(".pdf") else [Image.open(file_path)]

    for img in images:
        text += pytesseract.image_to_string(img)

    invoice_number = re.search(r'Invoice\s*(?:No|Number|#)\s*[:\-]?\s*([A-Za-z0-9\-]+)', text, re.IGNORECASE)
    date = re.search(r'Date\s*[:\-]?\s*([\d]{2}[-/][\d]{2}[-/][\d]{4})', text, re.IGNORECASE)
    total = re.findall(r'Total\s*(?:Amount)?\s*[:₹]?\s*([\d,]+)', text, re.IGNORECASE)
    vendor_name = re.search(r'^(.*?)\n', text)
    bill_to = re.search(r'Bill To:\s*(.*?)\n\n', text, re.DOTALL)
    ship_to = re.search(r'Ship To:\s*(.*?)\n\n', text, re.DOTALL)
    subtotal = re.search(r'Subtotal\s*[:₹]?\s*([\d,]+)', text, re.IGNORECASE)
    tax = re.search(r'Tax.*?\s*[:₹]?\s*([\d,]+)', text, re.IGNORECASE)

    data = {
        "invoice_number": invoice_number.group(1) if invoice_number else "Not Found",
        "date": date.group(1) if date else "Not Found",
        "total": total[-1].replace(",","") if total else "Not Found",
        "vendor_name": vendor_name.group(1).strip() if vendor_name else "Not Found",
        "bill_to": bill_to.group(1).strip() if bill_to else "Not Found",
        "ship_to": ship_to.group(1).strip() if ship_to else "Not Found",
        "subtotal": subtotal.group(1).replace(",","") if subtotal else "Not Found",
        "tax": tax.group(1).replace(",","") if tax else "Not Found"
    }

    confidence = {k: 100 if v!="Not Found" else 0 for k,v in data.items()}
    data["confidence"] = confidence
    return data