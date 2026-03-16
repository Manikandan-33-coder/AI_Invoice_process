# ml_model/layoutlm_extractor.py

from transformers import LayoutLMv3Processor, LayoutLMv3ForTokenClassification
from PIL import Image
import torch
import pdf2image

# Initialize processor and model
processor = LayoutLMv3Processor.from_pretrained("microsoft/layoutlmv3-base", apply_ocr=True)
model = LayoutLMv3ForTokenClassification.from_pretrained("microsoft/layoutlmv3-base", num_labels=9)

# Mapping from model output labels to invoice fields
FIELD_LABELS = {
    0: "O",
    1: "invoice_number",
    2: "date",
    3: "vendor_name",
    4: "bill_to",
    5: "ship_to",
    6: "subtotal",
    7: "tax",
    8: "total"
}


def ml_extract_fields(file_path):
    """
    Extract invoice fields from PDF or image using LayoutLMv3.

    Args:
        file_path (str): Path to invoice PDF or image.

    Returns:
        extracted_fields (dict): Extracted field values.
        confidence_scores (dict): Confidence % for each field.
    """

    # Load images from PDF or single image
    images = []
    if file_path.lower().endswith(".pdf"):
        images = pdf2image.convert_from_path(file_path, dpi=300)
    else:
        images = [Image.open(file_path)]

    extracted_fields = {}
    confidence_scores = {}

    for img in images:
        # Process image and get model outputs
        encoding = processor(img, return_tensors="pt")
        outputs = model(**encoding)
        logits = outputs.logits.squeeze(0)
        probs = torch.softmax(logits, dim=-1)

        # Get predicted label per token
        predictions = torch.argmax(probs, dim=-1).tolist()
        max_probs = torch.max(probs, dim=-1).tolist()

        # Decode tokens and map to fields
        for idx, label_id in enumerate(predictions):
            field = FIELD_LABELS.get(label_id, "O")
            if field != "O":
                token_text = processor.tokenizer.decode(encoding.input_ids[0][idx]).strip()
                if field in extracted_fields:
                    extracted_fields[field] += " " + token_text
                    confidence_scores[field] = max(confidence_scores[field], max_probs[idx])
                else:
                    extracted_fields[field] = token_text
                    confidence_scores[field] = max_probs[idx]

    # Fill missing fields
    for f in FIELD_LABELS.values():
        if f != "O" and f not in extracted_fields:
            extracted_fields[f] = "Not Found"
            confidence_scores[f] = 0.0

    # Convert confidence to percentage
    for k in confidence_scores:
        confidence_scores[k] = round(confidence_scores[k] * 100, 2)

    return extracted_fields, confidence_scores