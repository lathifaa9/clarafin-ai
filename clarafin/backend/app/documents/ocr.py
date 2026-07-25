import logging

logger = logging.getLogger("ocr")

def run_ocr_on_pdf_page(pdf_page) -> str:
    """
    Attempts OCR using pytesseract or easyocr fallback on a given pdfplumber page.
    """
    try:
        import pytesseract
        img = pdf_page.to_image(resolution=150).original
        return pytesseract.image_to_string(img)
    except Exception as e:
        logger.warning(f"pytesseract OCR failed: {e}. Trying easyocr fallback...")
        try:
            import easyocr
            import numpy as np
            img = pdf_page.to_image(resolution=150).original
            reader = easyocr.Reader(['en'], gpu=False)
            result = reader.readtext(np.array(img), detail=0)
            return "\n".join(result)
        except Exception as e2:
            logger.error(f"easyocr fallback failed: {e2}")
            return ""
