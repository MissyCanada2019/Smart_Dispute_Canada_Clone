import os
from docx import Document

try:
    from docx2pdf import convert as docx2pdf_convert
except ImportError:
    docx2pdf_convert = None

try:
    import pypandoc
except ImportError:
    pypandoc = None

def generate_legal_form(form_info, user_data, case_data):
    """
    Fill and export a form based on user/case info.

    Args:
        form_info (dict): from form_selector (form_file, court, name, notes)
        user_data (dict): from User model (name, phone, etc.)
        case_data (dict): from Case or Evidence (title, issue, AI tags)

    Returns:
        tuple: (filled_docx_path, filled_pdf_path or None)
    """
    form_file = form_info.get("form_file")
    province = user_data.get("province", "ON")
    template_path = os.path.join("templates", "forms", province, form_file)

    if not os.path.exists(template_path):
        print(f"Template not found at: {template_path}, using fallback.")
        template_path = os.path.join("templates", "forms", "base_form.docx")

    doc = Document(template_path)

    # Replace placeholders in paragraphs
    for para in doc.paragraphs:
        for key, val in {**user_data, **case_data}.items():
            placeholder = f"[{key.upper()}]"
            if placeholder in para.text:
                para.text = para.text.replace(placeholder, str(val))

    # Save output DOCX
    output_dir = "generated_forms"
    os.makedirs(output_dir, exist_ok=True)
    output_name = f"case_{case_data.get('id')}_{form_file}"
    docx_path = os.path.join(output_dir, output_name)
    doc.save(docx_path)

    # Try converting to PDF
    pdf_path = docx_path.replace(".docx", ".pdf")
    try:
        if docx2pdf_convert:
            docx2pdf_convert(docx_path, pdf_path)
        elif pypandoc:
            pypandoc.convert_file(docx_path, "pdf", outputfile=pdf_path)
        else:
            print("PDF conversion not supported.")
            pdf_path = None
    except Exception as e:
        print(f"PDF conversion error: {e}")
        pdf_path = None

    return docx_path, pdf_path
