import os

from flask import Flask, jsonify, render_template, request, send_file, send_from_directory

from modules.data_extractor import procesar_tabla
from modules.excel_export import crear_excel
from modules.pdf_processor import convertir_pdf, extraer_texto

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["OUTPUT_FOLDER"] = OUTPUT_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    archivo = request.files.get("archivo")

    if not archivo or archivo.filename == "":
        return "No seleccionaste ningún archivo"

    ruta_pdf = os.path.join(app.config["UPLOAD_FOLDER"], archivo.filename)
    archivo.save(ruta_pdf)

    paginas = convertir_pdf(ruta_pdf)
    texto = extraer_texto(ruta_pdf)
    modo = request.form.get("modo", "tabla").lower()

    encabezados = []
    tabla = []

    if modo == "texto":
        encabezados = ["Texto"]
        tabla = [{"Texto": texto}]
        crear_excel(encabezados, tabla, tipo="texto")
    else:
        encabezados, tabla = procesar_tabla(texto)
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
    )


@app.route("/guardar_correcciones", methods=["POST"])
def guardar_correcciones():
    datos = request.get_json(silent=True) or {}
    tipo = datos.get("tipo", "tabla")

    if tipo == "texto":
        texto = datos.get("texto", "")
        encabezados = ["Texto"]
        tabla = [{"Texto": texto}]
    else:
        encabezados = datos.get("encabezados", [])
        tabla = datos.get("tabla", [])

    crear_excel(encabezados, tabla, tipo=tipo)
    return jsonify({"ok": True, "archivo": "resultado_archivia.xlsx"})


@app.route("/descargar_excel")
def descargar_excel():
    return send_file(
        os.path.join(OUTPUT_FOLDER, "resultado_archivia.xlsx"),
        as_attachment=True,
        download_name="resultado_archivia.xlsx",
    )


@app.route("/outputs/<archivo>")
def outputs(archivo):
    return send_from_directory(OUTPUT_FOLDER, archivo)


if __name__ == "__main__":
    app.run(debug=True)
