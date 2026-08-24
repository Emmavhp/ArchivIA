import os

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