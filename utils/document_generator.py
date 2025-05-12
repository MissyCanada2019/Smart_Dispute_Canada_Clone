# utils/document_generator.py

import os
from docx import Document
import requests

def download_form_if_url(form_file):
    if form_file.startswith("http"):
        filename = form_file.split("/")[-1]
        path = os.path.join("templates/forms/federal/", filename)
        os.makedirs(os.path.dirname(path), exist_ok=True)

        if not os.path.exists(path):
            r = requests.get(form_file)
            with open(path, "wb") as f:
                f.write(r.content)
        return path
    return os.path.join("templates/forms/ON", form_file)

def generate_legal_form(form_info, user_data, case_data):
    form_path = download_form_if_url(form_info["form_file"])

    doc = Document(form_path)
    for para in doc.paragraphs:
        for key, val in {**user_data, **case_data}.items():
            placeholder = f"[{key.upper()}]"
            if placeholder in para.text:
                para.text = para.text.replace(placeholder, str(val))

    output_dir = "generated_forms"
    os.makedirs(output_dir, exist_ok=True)
    filename = f"case_{case_data.get('id')}_{form_info['form_name'].replace(' ', '_')}.docx"
    docx_path = os.path.join(output_dir, filename)
    doc.save(docx_path)

    return docx_path
