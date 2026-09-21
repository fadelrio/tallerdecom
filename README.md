# Sistema de comunicaciones digitales

Proyecto académico TA137: transmisión de un archivo de texto, según los
apartados A/B de la consigna. Se procesa texto por caracteres, no por bytes
UTF-8. Cada símbolo es un punto de código Unicode de Python `str`.

## Arquitectura

```text
.txt UTF-8 → lectura → análisis de caracteres → Huffman → bits
→ [futuro: codificación de canal, modulación, canal, demodulación]
→ decodificación Huffman → texto → escritura .txt UTF-8 → comparación
```

Se conservan mayúsculas, acentos, espacios, controles, BOM y saltos CR/LF/CRLF.
No se normaliza Unicode: `é` y `e` seguido de acento combinante son secuencias
distintas. Un emoji compuesto puede contener varios puntos de código.
La representación como bytes solo aparece al leer/escribir el archivo UTF-8.

## Estructura

- `main.py`: lectura, rechazo controlado del vacío, transmisión de fuente,
  recepción directa, escritura y comparación. Las etapas futuras son mensajes.
- `config.py`: `SimulationConfig`, rutas `entrada.txt` y `recibido.txt` junto
  al módulo; pueden editarse para elegir otros archivos.
- `common/data_types.py`: dataclasses compartidas.
- `common/file_utils.py`: lectura/escritura UTF-8 y comparación textual exacta.
- `common/report_utils.py`: impresión de tablas; preparación estructurada del
  informe todavía pendiente.
- `transmitter/source_analysis.py`: conteos, probabilidades y entropía.
- `transmitter/huffman.py`: árbol, código, estadísticas y eficiencia.
- `transmitter/source_encoder.py`: codificación por bloques de 65536 caracteres.
- `receiver/source_decoder.py`: reconstrucción de texto desde los bits.
- `tests/`: pruebas automáticas; `pytest.ini` limita su recolección a esta carpeta.
- `experiments/`: scripts manuales; `test_B.py` conserva su estilo original,
  adaptado únicamente a claves de caracteres y resultado `str`.
- `requirements.txt`: pytest; el programa usa la biblioteca estándar.
- `ENTORNO.md`: preparación del entorno sin depender de ningún editor o agente.
- Los `__init__.py` identifican paquetes; cada paquete tiene su propio README.

## Contratos de fuente

`read_file(Path) -> str`, `analyze_source(str) -> SourceStatistics`,
`build_huffman_code(dict[str, float]) -> HuffmanResult`,
`encode_source(str, dict[str, str]) -> EncodedSource`,
`decode_source(EncodedSource, dict[str, str]) -> str`,
`write_file(Path, str) -> None` y `compare_data(str, str) -> FileComparison`.

Los conteos, probabilidades y códigos usan caracteres como claves. Los tamaños
se expresan en caracteres. `EncodedSource.bits` contiene la secuencia binaria;
`list(encoded.iter_codewords(codebook))` permite obtener el vector de palabras
por carácter solicitado en B.6, sin almacenarlo también durante la transmisión.
La decodificación devuelve `str`, que ya se puede imprimir directamente.

La codificación limita la lista temporal por bloque, pero conserva toda la
entrada y salida en memoria. No es streaming ni empaquetado de bits. No se
hicieron mediciones de tiempo o memoria.

## Métricas y referencia de 8 bits

`minimum_length: float` representa H(X), límite inferior teórico del promedio.
No es la palabra más corta ni siempre es alcanzable por Huffman símbolo a
símbolo. `average_length` es el promedio real; la eficiencia es H(X)/promedio.
Para símbolo único se usa "0": entropía 0 y promedio 1.

La referencia fija de la consigna es 8 bits por carácter, distinta del tamaño
del archivo UTF-8. Solo es representable si todos los caracteres pertenecen a
la tabla de 8 bits elegida. La consigna no identifica qué "ASCII extendido"
utilizar: esa tabla debe acordarse antes de implementar `build_coding_report`.
No se calculan aún métricas de referencia para Unicode arbitrario ni se
reemplazan caracteres que no puedan representarse.

## Estado

### Apartado A

- [x] Arquitectura, configuración y orquestador.
- [x] Lectura y escritura textual UTF-8 sin traducción de saltos de línea.
- [x] Rechazo controlado de archivo vacío y comparación textual.

### Apartado B

- [x] Análisis de caracteres, probabilidades y entropía.
- [x] Huffman, mínimo promedio teórico, promedio, varianza y propiedad prefijo.
- [x] Eficiencia, codificación, decodificación y archivo recibido.
- [x] Acceso a palabras binarias por carácter e impresión de tablas.
- [ ] Preparación estructurada de las tablas del informe.
- [ ] Selección explícita de la tabla de referencia de 8 bits.
- [ ] Completar validaciones de códigos malformados del decodificador.

### Etapas futuras

- [ ] Codificación y decodificación de canal.
- [ ] Modulación y demodulación.
- [ ] AWGN y respuesta impulsiva.

## Ejecución y tests

Requiere Python 3.10 o posterior. Ver [ENTORNO.md](ENTORNO.md).

```bash
python main.py
python -m pytest -q -rs
python -m experiments.test_B
```

Si no existe la entrada, el principal muestra el recorrido conceptual. Si está
vacía o no es UTF-8 válido, muestra un error y no escribe salida. No permite
que las rutas resueltas de entrada y salida sean iguales. La salida configurada
se sobrescribe cuando la ejecución es válida.

Las pruebas verifican contratos, Unicode, acentos, controles, bloques, errores,
ida y vuelta y E/S textual. Los experimentos manuales se documentan en
[experiments/README.md](experiments/README.md).

## Mantenimiento

Actualizar código, pruebas, docstrings y README juntos. No marcar como
implementadas interfaces que solo lanzan `NotImplementedError`.
