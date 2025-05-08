# utils/document_generator.py

import os
from docx import Document
from docx2pdf import convert

def generate_legal_form(issue_category, province, user_data, case_id):
    """
    Generate a legal form .docx and .pdf pre-filled with user data.

    Args:
        issue_category (str): Legal category (e.g., 'Landlord-Tenant Dispute')
        province (str): Province code (e.g., 'ON', 'BC')
        user_data (dict): Dictionary with keys like FULL_NAME, ADDRESS, etc.
        case_id (int): Case ID to customize file names

    Returns:
        tuple: Paths to generated .docx and .pdf files
    """
    # Construct template path based on province and issue
    issue_slug = issue_category.replace(' ', '_').lower()
    template_path = f"templates/forms/{province}/{issue_slug}.docx"
    
    if not os.path.exists(template_path):
        template_path = "templates/forms/base_form.docx"

    doc = Document(template_path)

    # Replace placeholders in paragraphs
    for para in doc.paragraphs:
        for key, value in user_data.items():
            para.text = para.text.replace(f"[{key}]", str(value))

    # Save .docx file
    output_dir = "generated_forms"
    os.makedirs(output_dir, exist_ok=True)
    docx_path = os.path.join(output_dir, f"case_{case_id}_form.docx")
    doc.save(docx_path)

    # Convert to .pdf if possible
    pdf_path = docx_path.replace(".docx", ".pdf")
    try:
        convert(docx_path, pdf_path)
    except Exception as e:
        pdf_path = None
        print(f"PDF conversion failed: {e}")

    return docx_path, pdf_path
