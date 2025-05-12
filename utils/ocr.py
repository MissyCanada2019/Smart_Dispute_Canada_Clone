import os
import pytesseract
from PIL import Image
import fitz  # PyMuPDF
import docx
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_text_from_image(file_path):
    try:
        image = Image.open(file_path)
        return pytesseract.image_to_string(image).strip()
    except Exception as e:
        logger.error(f"Error reading image: {e}")
        return ""

def extract_text_from_pdf(file_path):
    try:
        text = ""
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text()
        return text.strip()
    except Exception as e:
        logger.error(f"Error reading PDF: {e}")
        return ""

def extract_text_from_docx(file_path):
    try:
        doc = docx.Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs]).strip()
    except Exception as e:
        logger.error(f"Error reading DOCX: {e}")
        return ""

def extract_text_from_txt(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception as e:
        logger.error(f"Error reading TXT: {e}")
        return ""

def extract_text_from_file(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext in [".jpg", ".jpeg", ".png"]:
        return extract_text_from_image(file_path), "image"
    elif ext == ".pdf":
        return extract_text_from_pdf(file_path), "pdf"
    elif ext == ".docx":
        return extract_text_from_docx(file_path), "docx"
    elif ext == ".txt":
        return extract_text_from_txt(file_path), "txt"
    else:
        logger.warning(f"Unsupported file type: {ext}")
        return "", "unsupported"
