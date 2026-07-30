import fitz
import os
from shutil import which

OUTPUT_FOLDER = "outputs"


def _find_tesseract_cmd():
    env_cmd = os.environ.get("TESSERACT_CMD") or os.environ.get("TESSERACT_PATH")
    if env_cmd and os.path.exists(env_cmd):
        return env_cmd

    system_cmd = which("tesseract")
    if system_cmd:
        return system_cmd

    common_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        "/usr/bin/tesseract",
        "/usr/local/bin/tesseract",
    ]

    for path in common_paths:
        if os.path.exists(path):
            return path

    return None

try:
    import pytesseract
    from PIL import Image
    TESSERACT_CMD = _find_tesseract_cmd()
    if TESSERACT_CMD:
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD
        OCR_AVAILABLE = True
    else:
        OCR_AVAILABLE = False
except ImportError:
    OCR_AVAILABLE = False


def _extraer_texto_ocr(pagina, dpi=300):
    pix = pagina.get_pixmap(dpi=dpi)
    img_format = "RGB" if pix.alpha == 0 else "RGBA"
    image = Image.frombytes(img_format, [pix.width, pix.height], pix.samples)
    if image.mode != "RGB":
        image = image.convert("RGB")
    try:
        return pytesseract.image_to_string(image, lang="spa")
    except Exception:
        return pytesseract.image_to_string(image)


def extraer_texto(pdf):
    documento = fitz.open(pdf)
    texto_paginas = []
    paginas_sin_texto = []

    for numero, pagina in enumerate(documento):
        contenido = pagina.get_text("text").strip()

        if contenido:
            texto_paginas.append(f"--- Página {numero+1} ---\n{contenido}")
        elif OCR_AVAILABLE:
            ocr_texto = _extraer_texto_ocr(pagina).strip()
            if ocr_texto:
                texto_paginas.append(f"--- Página {numero+1} ---\n{ocr_texto}")
            else:
                paginas_sin_texto.append(numero + 1)
        else:
            paginas_sin_texto.append(numero + 1)

    documento.close()
    texto = "\n\n".join(texto_paginas).strip()
    return texto, paginas_sin_texto


os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def convertir_pdf(pdf_path, dpi=300):

    documento = fitz.open(pdf_path)

    paginas = []

    for numero in range(documento.page_count):

        pagina = documento.load_page(numero)

        pix = pagina.get_pixmap(dpi=dpi)

        nombre = f"pagina_{numero+1}.png"

        ruta = os.path.join(OUTPUT_FOLDER, nombre)

        pix.save(ruta)

        paginas.append({
            "numero": numero + 1,
            "nombre": nombre,
            "ruta": ruta
        })

    documento.close()

    return paginas