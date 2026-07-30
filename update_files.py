from pathlib import Path

files = {
    'app.py': '''import os

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
''',
    'modules/data_extractor.py': '''import re


def detectar_columnas(texto):
    filas = []
    if not texto:
        return filas

    for linea in texto.splitlines():
        linea = linea.strip()
        if not linea:
            continue

        if "|" in linea:
            partes = [parte.strip() for parte in linea.split("|") if parte.strip()]
        else:
            partes = re.split(r"\t+|\s{2,}", linea)
            partes = [parte.strip() for parte in partes if parte.strip()]

        if len(partes) >= 2:
            filas.append(partes)

    return filas


def limpiar_nombre(nombre):
    texto = re.sub(r"[^a-zA-Z0-9]+", " ", nombre).strip()
    return texto.title() if texto else "Columna"


def separar_encabezado(filas):
    if not filas:
        return [], []

    primera = filas[0]
    palabras = " ".join(primera).lower()

    palabras_clave = [
        "nombre",
        "codigo",
        "código",
        "fecha",
        "producto",
        "cantidad",
        "precio",
        "valor",
        "total",
        "curso",
        "nota",
        "cliente",
        "direccion",
        "email",
        "monto",
    ]

    tiene_encabezado = any(palabra in palabras for palabra in palabras_clave)

    if tiene_encabezado:
        encabezados = [limpiar_nombre(col) for col in primera]
        datos = filas[1:]
    else:
        encabezados = []
        datos = filas

    return encabezados, datos


def procesar_tabla(texto):
    filas = detectar_columnas(texto)
    encabezados, datos = separar_encabezado(filas)

    tabla = []
    for fila in datos:
        registro = {}
        if encabezados:
            for i, valor in enumerate(fila):
                nombre = encabezados[i] if i < len(encabezados) else f"Columna {i + 1}"
                registro[nombre] = valor
        else:
            for i, valor in enumerate(fila):
                registro[f"Columna {i + 1}"] = valor
        tabla.append(registro)

    return encabezados or [f"Columna {i + 1}" for i in range(len(tabla[0]) if tabla else 0)], tabla
''',
    'modules/excel_export.py': '''import os

from openpyxl import Workbook


def crear_excel(encabezados, tabla, tipo="tabla"):
    libro = Workbook()
    hoja = libro.active
    hoja.title = "ArchivIA"

    if tipo == "texto":
        encabezados = ["Texto"]
        datos = []
        if tabla:
            datos = [fila.get("Texto", "") for fila in tabla]
        hoja.append(encabezados)
        for valor in datos:
            hoja.append([valor])
    else:
        columnas = encabezados or [f"Columna {i + 1}" for i in range(4)]
        hoja.append(columnas)
        for fila in tabla:
            if isinstance(fila, dict):
                valores = [fila.get(col, "") for col in columnas]
            else:
                valores = list(fila)
            hoja.append(valores)

    ruta = os.path.join("outputs", "resultado_archivia.xlsx")
    libro.save(ruta)
    return ruta
''',
    'templates/index.html': '''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>ArchivIA</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <div class="contenedor">
        <h1>📄 ArchivIA</h1>
        <p>Convierte tus PDFs en tabla o texto editable con exportación a Excel.</p>

        <form action="/upload" method="POST" enctype="multipart/form-data">
            <label class="grupo">
                <span>¿Qué quieres obtener?</span>
                <select name="modo">
                    <option value="tabla">Tabla estructurada</option>
                    <option value="texto">Texto suelto</option>
                </select>
            </label>

            <label class="grupo">
                <span>Sube tu PDF</span>
                <input type="file" name="archivo" accept=".pdf" required>
            </label>

            <button type="submit">Procesar PDF</button>
        </form>
    </div>
</body>
</html>
''',
    'templates/resultado.html': '''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>ArchivIA</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body data-tipo="{{ modo }}">
    <div class="contenedor resultado">
        <h1>📄 ArchivIA</h1>
        <h2>Resultado generado</h2>
        <p>Haz clic en cualquier celda para corregir datos y guarda los cambios antes de exportar.</p>

        <div class="acciones">
            <button id="guardar-cambios">💾 Guardar correcciones</button>
            <a href="/descargar_excel" class="boton-link">📥 Descargar Excel</a>
        </div>

        <input id="buscar" placeholder="Buscar información...">

        {% if modo == "texto" %}
            <textarea id="texto-editable">{{ texto }}</textarea>
        {% else %}
            <table id="tabla-datos">
                <thead>
                    <tr>
                        {% if encabezados %}
                            {% for titulo in encabezados %}
                                <th data-header="{{ titulo }}">{{ titulo }}</th>
                            {% endfor %}
                        {% else %}
                            <th>Columna 1</th><th>Columna 2</th><th>Columna 3</th><th>Columna 4</th>
                        {% endif %}
                    </tr>
                </thead>
                <tbody>
                    {% for fila in tabla %}
                        <tr>
                            {% for valor in fila.values() %}
                                <td contenteditable="true">{{ valor }}</td>
                            {% endfor %}
                        </tr>
                    {% endfor %}
                </tbody>
            </table>
        {% endif %}

        <hr>
        <h2>Documento original</h2>
        {% for pagina in paginas[:5] %}
            <img src="/outputs/{{ pagina.nombre }}" width="500">
            <br>
        {% endfor %}
    </div>

    <script src="{{ url_for('static', filename='js/script.js') }}"></script>
</body>
</html>
''',
    'static/css/style.css': '''body {
    background: #f3f5f7;
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 24px;
    color: #1f2937;
}

.contenedor {
    background: white;
    padding: 32px;
    border-radius: 16px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.12);
    width: min(900px, 100%);
    margin: 0 auto;
    text-align: center;
}

.resultado {
    text-align: left;
}

.grupo {
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin: 16px 0;
    text-align: left;
}

select, input[type="file"], textarea, table {
    width: 100%;
    padding: 10px;
    border-radius: 8px;
    border: 1px solid #d1d5db;
}

textarea {
    min-height: 220px;
    resize: vertical;
}

button, .boton-link {
    margin-top: 12px;
    padding: 12px 20px;
    border: none;
    background: #2563eb;
    color: white;
    font-size: 15px;
    border-radius: 8px;
    cursor: pointer;
    text-decoration: none;
    display: inline-block;
}

button:hover, .boton-link:hover {
    background: #1d4ed8;
}

.acciones {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin-bottom: 16px;
}

#tabla-datos {
    border-collapse: collapse;
    margin-top: 12px;
}

#tabla-datos th, #tabla-datos td {
    border: 1px solid #d1d5db;
    padding: 10px;
    min-width: 120px;
}

#tabla-datos th {
    background: #eff6ff;
}

#buscar {
    margin: 12px 0;
}

img {
    max-width: 100%;
    margin-bottom: 12px;
}
''',
    'static/js/script.js': '''document.addEventListener('DOMContentLoaded', () => {
    const buscar = document.getElementById('buscar');
    const guardar = document.getElementById('guardar-cambios');
    const tipo = document.body.dataset.tipo || 'tabla';

    if (buscar) {
        buscar.addEventListener('keyup', () => {
            const filtro = buscar.value.toLowerCase();
            const filas = document.querySelectorAll('#tabla-datos tbody tr');
            filas.forEach((fila) => {
                const texto = fila.innerText.toLowerCase();
                fila.style.display = texto.includes(filtro) ? '' : 'none';
            });
        });
    }

    if (guardar) {
        guardar.addEventListener('click', async () => {
            let payload = { tipo };

            if (tipo === 'texto') {
                payload.texto = document.getElementById('texto-editable')?.value || '';
            } else {
                const headers = Array.from(document.querySelectorAll('#tabla-datos thead th')).map((th) => th.textContent.trim());
                payload.encabezados = headers;
                payload.tabla = Array.from(document.querySelectorAll('#tabla-datos tbody tr')).map((row) => {
                    const valores = Array.from(row.children).map((celda) => celda.textContent.trim());
                    return headers.reduce((acc, header, index) => {
                        acc[header] = valores[index] || '';
                        return acc;
                    }, {});
                });
            }

            const response = await fetch('/guardar_correcciones', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });

            const data = await response.json();
            if (data.ok) {
                alert('Correcciones guardadas y exportadas a Excel.');
            }
        });
    }
});
''',
    'requirements.txt': 'Flask\nopenpyxl\nPyMuPDF\n'
}

for rel_path, content in files.items():
    path = Path(rel_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')
