from PIL import Image, ImageDraw, ImageFont
import fitz
import os
from modules.pdf_processor import extraer_texto, OCR_AVAILABLE, TESSERACT_CMD

print('OCR_AVAILABLE', OCR_AVAILABLE)
print('TESSERACT_CMD', TESSERACT_CMD)

img = Image.new('RGB', (600, 200), color='white')
draw = ImageDraw.Draw(img)
try:
    font = ImageFont.truetype('arial.ttf', 24)
except Exception:
    font = ImageFont.load_default()
draw.text((20, 50), 'Prueba OCR ArchivIA', fill='black', font=font)
img_path = 'temp_ocr_test.png'
img.save(img_path)

pdf_path = 'temp_ocr_test.pdf'
if os.path.exists(pdf_path):
    os.remove(pdf_path)
doc = fitz.open()
rect = fitz.Rect(0, 0, img.width, img.height)
page = doc.new_page(width=img.width, height=img.height)
page.insert_image(rect, filename=img_path)
doc.save(pdf_path)
doc.close()

texto, paginas_sin_texto = extraer_texto(pdf_path)
print('texto extracted:', repr(texto))
print('paginas_sin_texto', paginas_sin_texto)

for filename in (img_path, pdf_path):
    if os.path.exists(filename):
        os.remove(filename)
