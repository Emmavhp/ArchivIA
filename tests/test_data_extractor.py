from modules.data_extractor import procesar_tabla


def test_procesar_tabla_detecta_encabezados_y_datos():
    texto = """Nombre Código Fecha\nJuan 001 2024-01-01\nAna 002 2024-01-02"""
    encabezados, tabla = procesar_tabla(texto)
    assert encabezados == ["Nombre", "Código", "Fecha"]
    assert len(tabla) == 2
    assert tabla[0]["columna1"] == "Juan"


def test_procesar_tabla_respecta_numero_de_columnas():
    texto = """Nombre Apellido
Juan Pérez
Ana Gómez"""
    encabezados, tabla = procesar_tabla(texto, numero_columnas=3)
    assert encabezados == ["Nombre", "Apellido", ""]
    assert len(tabla[0]) == 3
    assert tabla[0]["columna3"] == ""
