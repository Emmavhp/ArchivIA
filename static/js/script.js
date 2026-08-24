document.addEventListener('DOMContentLoaded', () => {
    const buscar = document.getElementById('buscar');
    const guardar = document.getElementById('guardar-cambios');
    const copiar = document.getElementById('copiar-texto');
    const tipo = document.body.dataset.tipo || 'tabla';
    const columnas = Number(document.body.dataset.columnas || 4);
    const textoOriginalElement = document.getElementById('texto-original');
    const textoOriginal = textoOriginalElement ? JSON.parse(textoOriginalElement.textContent) : '';
    const paginasOriginalesElement = document.getElementById('paginas-originales');
    const paginasOriginales = paginasOriginalesElement ? JSON.parse(paginasOriginalesElement.textContent) : [];
    let filaSeleccionada = null;
    let menuContextual = null;

    if (tipo === 'texto') {
        const selectorPagina = document.getElementById('pagina-texto');
        const imagenPagina = document.getElementById('imagen-pagina-texto');
        const textoEditable = document.getElementById('texto-editable');
        const estadoPagina = document.getElementById('estado-pagina-texto');
        const paginasTexto = {};
        textoOriginal.split(/(?=--- Página \d+ ---)/).filter((pagina) => pagina.trim()).forEach((pagina) => {
            const numero = pagina.match(/--- Página (\d+) ---/)?.[1];
            if (numero) paginasTexto[numero] = pagina.replace(/^--- Página \d+ ---\s*/, '');
        });
        const paginas = paginasOriginales.length ? paginasOriginales : [{ numero: 1, nombre: 'pagina_1.png' }];
        let paginaActual = Number(selectorPagina?.value || paginas[0].numero);

        function actualizarPaginaTexto(numero) {
            paginaActual = Number(numero) || 1;
            const pagina = paginas.find((item) => Number(item.numero) === paginaActual);
            imagenPagina.src = `/outputs/${pagina?.nombre || `pagina_${paginaActual}.png`}`;
            imagenPagina.alt = `Página ${paginaActual} del documento`;
            textoEditable.value = paginasTexto[paginaActual] || '';
            if (estadoPagina) {
                estadoPagina.textContent = `Página ${paginaActual} de ${paginas.length}. El texto se puede editar sobre la imagen.`;
            }
        }

        selectorPagina?.addEventListener('change', (event) => actualizarPaginaTexto(event.target.value));
        actualizarPaginaTexto(paginaActual);

        window.obtenerTextoCompleto = () => {
            paginasTexto[paginaActual] = textoEditable.value;
            return paginas.map((pagina) => `--- Página ${pagina.numero} ---\n${paginasTexto[pagina.numero] || ''}`).join('\n\n').trim();
        };
    }

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
        const crearMenuContextual = () => {
            if (menuContextual) return menuContextual;
            menuContextual = document.createElement('div');
            menuContextual.id = 'menu-contextual-tabla';
            menuContextual.innerHTML = `
                <button type="button" data-accion="copiar">📋 Copiar</button>
                <button type="button" data-accion="celda">➡️ Enviar a celda</button>
            `;
            document.body.appendChild(menuContextual);
            return menuContextual;
        };

        const ocultarMenuContextual = () => {
            if (menuContextual) {
                menuContextual.style.display = 'none';
            }
        };

        document.querySelectorAll('#tabla-datos td').forEach((celda) => {
            celda.addEventListener('mouseup', (event) => {
                const seleccion = window.getSelection()?.toString().trim();
                if (!seleccion) return;
                const menu = crearMenuContextual();
                menu.style.display = 'flex';
                menu.style.position = 'fixed';
                menu.style.left = `${event.clientX}px`;
                menu.style.top = `${event.clientY}px`;
                menu.dataset.texto = seleccion;
                menu.dataset.celda = Array.from(celda.parentElement.children).indexOf(celda);
            });
        });

        document.addEventListener('mousedown', (event) => {
            if (menuContextual && !menuContextual.contains(event.target)) {
                ocultarMenuContextual();
            }
        });

        document.addEventListener('click', (event) => {
            const boton = event.target.closest('#menu-contextual-tabla button');
            if (!boton || !menuContextual) return;
            const texto = menuContextual.dataset.texto || '';
            const index = Number(menuContextual.dataset.celda || 0);
            if (boton.dataset.accion === 'copiar') {
                navigator.clipboard.writeText(texto).catch(() => {});
                alert('Texto copiado al portapapeles.');
            } else if (boton.dataset.accion === 'celda') {
                const fila = filaSeleccionada || document.querySelector('#tabla-datos tbody tr');
                if (!fila) {
                    alert('Selecciona una fila primero.');
                    return;
                }
                const celdas = fila.querySelectorAll('td');
                if (index < 0 || index >= celdas.length) {
                    alert('No se pudo asignar a la celda seleccionada.');
                    return;
                }
                celdas[index].textContent = texto;
                alert('Texto asignado a la celda.');
            }
            ocultarMenuContextual();
        });

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
                payload.texto = window.obtenerTextoCompleto ? window.obtenerTextoCompleto() : document.getElementById('texto-editable')?.value || '';
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
                texto = window.obtenerTextoCompleto ? window.obtenerTextoCompleto() : document.getElementById('texto-editable')?.value || '';
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
