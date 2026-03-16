from transformers import LayoutLMv3Processor, LayoutLMv3ForTokenClassification
from PIL import Image
import torch
import pdf2image

# Load processor and model
processor = LayoutLMv3Processor.from_pretrained(
    "microsoft/layoutlmv3-base",
    apply_ocr=True
)

model = LayoutLMv3ForTokenClassification.from_pretrained(
    "microsoft/layoutlmv3-base",
    num_labels=9
)

# Force CPU (Streamlit cloud has no GPU)
device = torch.device("cpu")
model.to(device)

# Label mapping
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
    Extract invoice fields from PDF or image using LayoutLMv3
    """

    images = []

    # Convert PDF → images
    if file_path.lower().endswith(".pdf"):
        images = pdf2image.convert_from_path(file_path, dpi=300)
    else:
        images = [Image.open(file_path).convert("RGB")]

    extracted_fields = {}
    confidence_scores = {}

    for img in images:

        encoding = processor(img, return_tensors="pt")

        # Move tensors to CPU
        encoding = {k: v.to(device) for k, v in encoding.items()}

        # Model inference
        with torch.no_grad():
            outputs = model(**encoding)

        logits = outputs.logits[0]

        probs = torch.softmax(logits, dim=-1)

        predictions = torch.argmax(probs, dim=-1)
        max_probs = torch.max(probs, dim=-1).values

        input_ids = encoding["input_ids"][0]

        for idx, label_id in enumerate(predictions):

            field = FIELD_LABELS.get(label_id.item(), "O")

            if field != "O":

                token_text = processor.tokenizer.decode(
                    [input_ids[idx]],
                    skip_special_tokens=True
                ).strip()

                if token_text == "":
                    continue

                if field in extracted_fields:
                    extracted_fields[field] += " " + token_text
                    confidence_scores[field] = max(
                        confidence_scores[field],
                        max_probs[idx].item()
                    )
                else:
                    extracted_fields[field] = token_text
                    confidence_scores[field] = max_probs[idx].item()

    # Fill missing fields
    for field in FIELD_LABELS.values():

        if field != "O" and field not in extracted_fields:
            extracted_fields[field] = "Not Found"
            confidence_scores[field] = 0.0

    # Convert confidence → percentage
    for key in confidence_scores:
        confidence_scores[key] = round(confidence_scores[key] * 100, 2)

    return extracted_fields, confidence_scores
