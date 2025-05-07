
def analyze_merit_weight(ocr_output):
    """
    Analyze the AI OCR output and assign a merit score (0-100)
    and a human-readable explanation for decision support.
    """
    score = 0
    notes = []

    # Example scoring based on simple heuristics in the OCR text
    ocr_text = str(ocr_output).lower()

    if "harassment" in ocr_text:
        score += 25
        notes.append("Keyword 'harassment' detected.")

    if "unlivable" in ocr_text or "unsafe" in ocr_text:
        score += 25
        notes.append("Conditions appear unsafe or unlivable.")

    if "ignored" in ocr_text or "no response" in ocr_text:
        score += 15
        notes.append("Lack of response from responsible party.")

    if "medical" in ocr_text or "health" in ocr_text:
        score += 20
        notes.append("Health/medical concern mentioned.")

    if "child" in ocr_text or "baby" in ocr_text:
        score += 15
        notes.append("Children involved, increases merit weight.")

    final_score = min(score, 100)
    return final_score, "; ".join(notes)
