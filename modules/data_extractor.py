import re


def detectar_columnas(texto, numero_columnas=None):
    filas = []
    lineas = texto.splitlines()

    for linea in lineas:
        linea = linea.strip()

        if linea == "":
            continue

        partes = re.split(r"\s{2,}", linea)

        if numero_columnas is not None:
            partes = partes[:numero_columnas]
            if len(partes) < numero_columnas:
                partes = partes + [""] * (numero_columnas - len(partes))
            filas.append(partes)
        elif len(partes) >= 2:
            filas.append(partes)

    return filas


def separar_encabezado(filas, numero_columnas=None):
    if len(filas) == 0:
        return [], []

    primera = list(filas[0])

    if numero_columnas is not None:
        primera = primera[:numero_columnas]
        if len(primera) < numero_columnas:
            primera = primera + [""] * (numero_columnas - len(primera))

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
    ]

    tiene_encabezado = any(palabra in palabras for palabra in palabras_clave)

    if tiene_encabezado:
        encabezados = primera
        datos = filas[1:]
    else:
        encabezados = []
        datos = filas

    if numero_columnas is not None:
        if not encabezados:
            encabezados = [f"Columna {i + 1}" for i in range(numero_columnas)]
        else:
            encabezados = encabezados[:numero_columnas]
            if len(encabezados) < numero_columnas:
                encabezados = encabezados + [""] * (numero_columnas - len(encabezados))

    return encabezados, datos


def procesar_tabla(texto, numero_columnas=None):
    filas = detectar_columnas(texto, numero_columnas=numero_columnas)
    encabezados, datos = separar_encabezado(filas, numero_columnas=numero_columnas)

    tabla = []

    for fila in datos:
        registro = {}
        for i, valor in enumerate(fila):
            clave = encabezados[i] if encabezados and i < len(encabezados) and encabezados[i] else f"columna{i + 1}"
            registro[clave] = valor
        tabla.append(registro)

    return encabezados, tabla
