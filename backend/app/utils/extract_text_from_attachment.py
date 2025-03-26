import io
import pdfplumber
from PIL import Image
import pytesseract

def extract_text_from_attachment(filename, content):
    """Extract text from a PDF or image attachment."""
    text = ""
    
    if filename.endswith(".pdf"):
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
    
    elif filename.endswith((".jpg", ".png", ".jpeg")):
        image = Image.open(io.BytesIO(content))
        # Apply OCR to extract text from image
        text = pytesseract.image_to_string(image, config="--psm 6")  # "6" improves block text recognition

    return text.strip()