import json
import os

from flask import Flask, jsonify, render_template, request, send_file, send_from_directory

from modules.data_extractor import procesar_tabla
from modules.excel_export import crear_excel
from modules.pdf_processor import convertir_pdf, extraer_texto, OCR_AVAILABLE


app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["OUTPUT_FOLDER"] = OUTPUT_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def _parse_numero_columnas(valor):
    try:
        numero = int(valor)
    except (TypeError, ValueError):
        return 4
    return max(1, numero)


def _guardar_json(encabezados, tabla):
    ruta = os.path.join(OUTPUT_FOLDER, "resultado_archivia.json")
    with open(ruta, "w", encoding="utf-8") as archivo:
        json.dump({"encabezados": encabezados, "tabla": tabla}, archivo, ensure_ascii=False, indent=2)
    return ruta


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    archivo = request.files.get("archivo")

    if not archivo or archivo.filename == "":
        return "No seleccionaste ningún archivo"

    modo = request.form.get("modo", "tabla").lower()
    numero_columnas = _parse_numero_columnas(request.form.get("numero_columnas"))

    ruta_pdf = os.path.join(app.config["UPLOAD_FOLDER"], archivo.filename)
    archivo.save(ruta_pdf)

    paginas = convertir_pdf(ruta_pdf)
    texto, paginas_sin_texto = extraer_texto(ruta_pdf)

    advertencia = None
    if paginas_sin_texto:
        paginas_lista = ", ".join(str(num) for num in paginas_sin_texto)
        if OCR_AVAILABLE:
            advertencia = (
                f"No se detectó texto en las páginas {paginas_lista}. "
                "Puede que el PDF contenga imágenes o texto no reconocible."
            )
        else:
            advertencia = (
                f"No se detectó texto en las páginas {paginas_lista}. "
                "OCR no está disponible; instala pytesseract y Tesseract OCR para habilitarlo."
            )

    encabezados = []
    tabla = []

    if modo == "texto":
        encabezados = ["Texto"]
        tabla = [{"Texto": texto}]
        crear_excel(encabezados, tabla, tipo="texto")
    elif modo == "json":
        encabezados, tabla = procesar_tabla(texto, numero_columnas=numero_columnas)
        _guardar_json(encabezados, tabla)
    else:
        encabezados, tabla = procesar_tabla(texto, numero_columnas=numero_columnas)
        crear_excel(encabezados, tabla, tipo="tabla")

    return render_template(
        "resultado.html",
        paginas=paginas,
        total=len(paginas),
        texto=texto,
        tabla=tabla,
        encabezados=encabezados,
        modo=modo,
        archivo=archivo.filename,
        numero_columnas=numero_columnas,
        json_data={"encabezados": encabezados, "tabla": tabla},
        advertencia=advertencia,
    )


@app.route("/guardar_correcciones", methods=["POST"])
def guardar_correcciones():
    datos = request.get_json(silent=True) or {}
    tipo = datos.get("tipo", "tabla")

    if tipo == "texto":
        texto = datos.get("texto", "")
        encabezados = ["Texto"]
        tabla = [{"Texto": texto}]
        crear_excel(encabezados, tabla, tipo="texto")
    elif tipo == "json":
        encabezados = datos.get("encabezados", [])
        tabla = datos.get("tabla", [])
        _guardar_json(encabezados, tabla)
    else:
        encabezados = datos.get("encabezados", [])
        tabla = datos.get("tabla", [])
        crear_excel(encabezados, tabla, tipo="tabla")

    return jsonify({"ok": True, "archivo": "resultado_archivia.json" if tipo == "json" else "resultado_archivia.xlsx"})


@app.route("/descargar_excel")
def descargar_excel():
    return send_file(
        os.path.join(OUTPUT_FOLDER, "resultado_archivia.xlsx"),
        as_attachment=True,
        download_name="resultado_archivia.xlsx",
    )


@app.route("/descargar_json")
def descargar_json():
    return send_file(
        os.path.join(OUTPUT_FOLDER, "resultado_archivia.json"),
        as_attachment=True,
        download_name="resultado_archivia.json",
    )


@app.route("/outputs/<archivo>")
def outputs(archivo):
    return send_from_directory(OUTPUT_FOLDER, archivo)


if __name__ == "__main__":
    app.run(debug=True)
