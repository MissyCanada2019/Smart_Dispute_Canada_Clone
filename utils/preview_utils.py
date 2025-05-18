from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io

def create_watermarked_preview(original_pdf_path, preview_pdf_path):
    reader = PdfReader(original_pdf_path)
    writer = PdfWriter()

    # Apply watermark and crop/blur effect to only the first page
    first_page = reader.pages[0]
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.setFont("Helvetica-Bold", 36)
    can.setFillGray(0.5, 0.5)
    can.drawCentredString(300, 400, "PREVIEW ONLY - UNLOCK FULL VERSION")
    can.save()

    packet.seek(0)
    watermark = PdfReader(packet).pages[0]
    first_page.merge_page(watermark)
    writer.add_page(first_page)

    # Add a blank page as a teaser (blur effect simulated)
    writer.add_blank_page(width=first_page.mediabox.width, height=first_page.mediabox.height)

    with open(preview_pdf_path, "wb") as output:
        writer.write(output)lol 
