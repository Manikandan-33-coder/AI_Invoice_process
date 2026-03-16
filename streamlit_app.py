import streamlit as st
import os
from extractor import extract_invoice_data
from ocr_extractor import extract_invoice_data_ocr

# Upload folder (Streamlit handles temp files automatically)
UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

st.set_page_config(page_title="AI Invoice Processor", layout="centered")
st.title("📄 AI-Powered Invoice Processing System")

# File uploader
uploaded_file = st.file_uploader("Upload Invoice PDF", type=["pdf"])

if uploaded_file:
    file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.info("Processing invoice...")

    # 1️⃣ Try ML + PDF extractor
    data = extract_invoice_data(file_path)

    # 2️⃣ If invoice number not found → fallback to OCR
    if data["invoice_number"] == "Not Found":
        st.warning("Using OCR fallback...")
        data = extract_invoice_data_ocr(file_path)

    st.success("Extraction Complete ✅")

    # Show results with confidence (if exists)
    st.subheader("Extracted Data")
    for field, value in data.items():
        st.write(f"**{field}:** {value}")

    # Save button (optional)
    if st.button("Save Invoice"):
        # Here, save to database or CSV
        st.success(f"Invoice {data.get('invoice_number', '')} saved successfully!")