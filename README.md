# Sistema de comunicaciones digitales

Proyecto académico TA137: transmisión de un archivo de texto, según los
apartados A/B de la consigna. Se procesa texto por caracteres, no por bytes
UTF-8. Cada símbolo es un punto de código Unicode de Python `str`.

## Arquitectura

```text
.txt UTF-8 → lectura → análisis de caracteres → Huffman → bits
→ conexión directa → decodificación Huffman → texto → escritura .txt UTF-8 → comparación
```

Se conservan mayúsculas, acentos, espacios, controles, BOM y saltos CR/LF/CRLF.
No se normaliza Unicode: `é` y `e` seguido de acento combinante son secuencias
distintas. Un emoji compuesto puede contener varios puntos de código.
La representación como bytes solo aparece al leer/escribir el archivo UTF-8.

## Estructura

- `main.py`: lectura, rechazo controlado del vacío, transmisión de fuente,
  recepción directa, escritura, comparación y tablas del apartado B.
- `config.py`: `SimulationConfig`, rutas `entrada.txt` y `recibido.txt` junto
  al módulo; pueden editarse para elegir otros archivos.
- `common/data_types.py`: dataclasses compartidas.
- `common/file_utils.py`: lectura/escritura UTF-8 y comparación textual exacta.
- `common/report_utils.py`: preparación y presentación de tablas y muestra
  de una línea para el informe, sin análisis ni conclusiones.
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
la tabla de 8 bits elegida. Se adopta explícitamente Windows-1252 (cp1252) para esta referencia.
Si hay caracteres fuera de esa tabla, el reporte indica "No aplicable" y
los enumera; el recorrido Huffman sigue funcionando con Unicode. El total
8*N en CodingReport es nominal cuando fixed_representable es False.

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
- [x] Preparación estructurada de las tablas del informe.
- [x] Referencia fija Windows-1252 de 8 bits identificada en la salida.
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

Si la entrada no existe, está vacía o no es UTF-8 válido, el principal
muestra un error y no escribe salida. No permite
que las rutas resueltas de entrada y salida sean iguales. La salida configurada
se sobrescribe cuando la ejecución es válida.

Las pruebas verifican contratos, Unicode, acentos, controles, bloques, errores,
ida y vuelta y E/S textual. Los experimentos manuales se documentan en
[experiments/README.md](experiments/README.md).

## Mantenimiento

Actualizar código, pruebas, docstrings y README juntos. No marcar como
implementadas interfaces que solo lanzan `NotImplementedError`.

## Datos para el informe B

Configurar `input_file` y `output_file` en `config.py` y ejecutar `python main.py`.
La salida se organiza en seis secciones:

1. Carácter escapado, identificador Unicode, cantidad, probabilidad, código y longitud.
2. Verificación de prefijo por pares, indicador del constructor, alfabeto y longitudes.
3. Entropía, mínimo promedio teórico, promedio real, varianza, eficiencia y código fijo.
4. Totales de bits Huffman y referencia fija (sin diccionario ni metadatos).
5. Primera línea completa, palabras binarias por carácter, bits concatenados y texto
   decodificado; se incluye el terminador y se muestran escapados los controles.
6. Igualdad de los textos y cantidades de caracteres, tras releer el archivo recibido.

Para guardar lo mostrado en un archivo independiente:

```bash
python main.py > datos_informe.md
```

Usar un destino distinto de la entrada y de `recibido.txt`. No se generan
conclusiones, interpretación de métricas ni documentos PDF/Word.

## Usar textos propios o descargados de Gutenberg

El programa acepta cualquier archivo local de texto UTF-8. No hay que cambiar
el algoritmo ni editar `config.py` para alternar entre fuentes:

```bash
python main.py --input "textos/mi texto.txt" --output "recibido_propio.txt"
python main.py --input "textos/pg12345.txt" --output "recibido_gutenberg.txt"
python main.py --help
```

Las rutas de ejemplo deben reemplazarse por las de los archivos que tengas.
En Gutenberg, descargar la versión de texto plano UTF-8 de la obra (no HTML,
EPUB ni ZIP) y pasar la ruta del `.txt` guardado a `--input`. La descarga se
hace manualmente; el programa no necesita Internet ni dependencias nuevas.
Si el archivo tiene otra codificación, convertir una copia a UTF-8 antes de
usarla; nunca se sustituyen silenciosamente los caracteres inválidos.

Se conserva todo el archivo, incluidos encabezado, licencia y controles.
Esos caracteres también participan en las estadísticas. Para estudiar solo
el cuerpo de la obra, preparar otra copia del TXT y usarla como entrada;
la comparación siempre se realiza contra esa entrada elegida.

Sin argumentos, se mantienen las rutas de `config.py`. Las rutas pasadas por
terminal se resuelven desde el directorio de trabajo. La carpeta de salida
debe existir y el archivo de salida no debe ser el original.

Para guardar las tablas de una ejecución:

```bash
python main.py --input "textos/pg12345.txt" --output "recibido_gutenberg.txt" > datos_gutenberg.md
```

Los libros completos pueden consumir bastante memoria: toda la fuente y la
cadena de bits se mantienen en memoria. El procesamiento por bloques limita
la lista temporal del codificador, pero no convierte el sistema en streaming.

## Salida Markdown

Las secciones y tablas del informe se imprimen en Markdown por consola.
Los símbolos especiales se escapan en las tablas y la muestra se incluye en
un bloque literal. No se crea automáticamente ningún archivo de informe.
El archivo recibido de la simulación sigue escribiéndose en `--output`.

```bash
# Ver el Markdown por consola
python main.py --input "mi_texto.txt" --output "recibido.txt"

# Guardar la salida cuando se desee
python main.py --input "mi_texto.txt" --output "recibido.txt" > informe.md
```

La redirección la realiza la terminal. `informe.md` debe ser distinto tanto del
archivo de entrada como del archivo recibido, porque `>` abre el destino antes
de que comience el programa.
