# utils/document_generator.py

import os
from docx import Document

# Optional: fallback converter
try:
    import pypandoc
except ImportError:
    pypandoc = None

# Primary converter
try:
    from docx2pdf import convert as docx2pdf_convert
except ImportError:
    docx2pdf_convert = None

def generate_legal_form(issue_category, province, user_data, case_id):
    """
    Generate a .docx and .pdf legal form customized with user details.

    Returns:
        tuple: (docx_path, pdf_path or None)
    """
    # Normalize issue for file naming
    issue_slug = issue_category.replace(" ", "_").lower()
    template_path = f"templates/forms/{province}/{issue_slug}.docx"
    if not os.path.exists(template_path):
        template_path = "templates/forms/base_form.docx"

    # Load and fill document
    doc = Document(template_path)
    for para in doc.paragraphs:
        for key, val in user_data.items():
            para.text = para.text.replace(f"[{key}]", str(val))

    # Save filled docx
    output_dir = "generated_forms"
    os.makedirs(output_dir, exist_ok=True)
    docx_path = os.path.join(output_dir, f"case_{case_id}_form.docx")
    doc.save(docx_path)

    # Attempt PDF conversion
    pdf_path = docx_path.replace(".docx", ".pdf")
    try:
        if docx2pdf_convert:
            docx2pdf_convert(docx_path, pdf_path)
        elif pypandoc:
            pypandoc.convert_file(docx_path, "pdf", outputfile=pdf_path)
        else:
            raise RuntimeError("No available PDF converter.")
    except Exception as e:
        print(f"PDF conversion failed: {e}")
        pdf_path = None

    return docx_path, pdf_path
