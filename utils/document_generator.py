from docx import Document
import os

def generate_legal_form(template_path, output_path, user_data):
    doc = Document(template_path)

    for paragraph in doc.paragraphs:
        for key, value in user_data.items():
            if f"[{key}]" in paragraph.text:
                paragraph.text = paragraph.text.replace(f"[{key}]", value)

    doc.save(output_path)
    return output_path
