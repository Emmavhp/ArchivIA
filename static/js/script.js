document.addEventListener('DOMContentLoaded', () => {
    const buscar = document.getElementById('buscar');
    const guardar = document.getElementById('guardar-cambios');
    const copiar = document.getElementById('copiar-texto');
    const tipo = document.body.dataset.tipo || 'tabla';
    const columnas = Number(document.body.dataset.columnas || 4);
    let filaSeleccionada = null;

    function crearFilaVacia() {
        const fila = document.createElement('tr');
        for (let i = 0; i < columnas; i += 1) {
            const celda = document.createElement('td');
            celda.contentEditable = 'true';
            fila.appendChild(celda);
        }
        return fila;
    }

    function actualizarSeleccionFila(fila) {
        if (!fila) return;
        document.querySelectorAll('#tabla-datos tbody tr').forEach((row) => {
            row.classList.toggle('fila-seleccionada', row === fila);
        });
        filaSeleccionada = fila;
    }

    if (tipo === 'tabla') {
        document.querySelectorAll('#tabla-datos tbody').forEach((tbody) => {
            tbody.addEventListener('click', (event) => {
                const fila = event.target.closest('tr');
                if (fila) {
                    actualizarSeleccionFila(fila);
                }
            });
        });

        const asignarBoton = document.getElementById('asignar-seleccion');
        const dividirBoton = document.getElementById('dividir-seleccion');
        const textoExtraido = document.getElementById('texto-extraido');
        const columnaDestino = document.getElementById('columna-destino');

        function obtenerTextoSeleccionado() {
            if (!textoExtraido) return '';
            return textoExtraido.value.substring(textoExtraido.selectionStart, textoExtraido.selectionEnd).trim();
        }

        function obtenerFilaDestino() {
            if (filaSeleccionada) {
                return filaSeleccionada;
            }
            const tbody = document.querySelector('#tabla-datos tbody');
            const nuevaFila = crearFilaVacia();
            tbody.appendChild(nuevaFila);
            actualizarSeleccionFila(nuevaFila);
            return nuevaFila;
        }

        function setCeldaTexto(fila, index, text) {
            const celdas = fila.querySelectorAll('td');
            if (index < 0 || index >= celdas.length) return;
            celdas[index].textContent = text;
        }

        function crearFilasDesdePartes(partes, startIndex) {
            const tbody = document.querySelector('#tabla-datos tbody');
            let fila = crearFilaVacia();
            tbody.appendChild(fila);
            let index = startIndex;

            partes.forEach((parte) => {
                if (index >= columnas) {
                    fila = crearFilaVacia();
                    tbody.appendChild(fila);
                    index = 0;
                }
                setCeldaTexto(fila, index, parte);
                index += 1;
            });

            actualizarSeleccionFila(fila);
            fila.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }

        if (asignarBoton) {
            asignarBoton.addEventListener('click', () => {
                const seleccion = obtenerTextoSeleccionado();
                if (!seleccion) {
                    alert('Selecciona el texto que quieres asignar.');
                    return;
                }
                const fila = obtenerFilaDestino();
                const index = Number(columnaDestino.value);
                setCeldaTexto(fila, index, seleccion);
                fila.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            });
        }

        if (dividirBoton) {
            dividirBoton.addEventListener('click', () => {
                const seleccion = obtenerTextoSeleccionado();
                if (!seleccion) {
                    alert('Selecciona el texto que quieres dividir.');
                    return;
                }
                const partes = seleccion.split(/\r?\n|\t| {2,}/).map((parte) => parte.trim()).filter(Boolean);
                if (!partes.length) {
                    alert('No se detectó texto válido para dividir.');
                    return;
                }
                const index = Number(columnaDestino.value);
                crearFilasDesdePartes(partes, index);
            });
        }
    }

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
            } else if (tipo === 'json') {
                const jsonData = document.getElementById('json-data');
                const parsed = jsonData ? JSON.parse(jsonData.textContent) : { encabezados: [], tabla: [] };
                payload.encabezados = parsed.encabezados || [];
                payload.tabla = parsed.tabla || [];
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
                alert(tipo === 'json' ? 'JSON guardado correctamente.' : 'Correcciones guardadas y exportadas.');
            }
        });
    }

    if (copiar) {
        copiar.addEventListener('click', async () => {
            let texto = '';

            if (tipo === 'texto') {
                texto = document.getElementById('texto-editable')?.value || '';
            } else if (tipo === 'json') {
                const jsonData = document.getElementById('json-data');
                texto = jsonData ? JSON.stringify(JSON.parse(jsonData.textContent), null, 2) : '';
            } else {
                const headers = Array.from(document.querySelectorAll('#tabla-datos thead th')).map((th) => th.textContent.trim());
                const filas = Array.from(document.querySelectorAll('#tabla-datos tbody tr'));
                texto = filas.map((row) => {
                    const valores = Array.from(row.children).map((celda) => celda.textContent.trim());
                    return valores.map((valor, index) => `${headers[index] || `Columna ${index + 1}`}: ${valor}`).join(' | ');
                }).join('\n');
            }

            if (!texto) {
                alert('No hay texto para copiar.');
                return;
            }

            try {
                await navigator.clipboard.writeText(texto);
                alert('Texto copiado al portapapeles.');
            } catch (error) {
                alert('No se pudo copiar el texto.');
            }
        });
    }
});
