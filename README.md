# Sistema de comunicaciones digitales

Proyecto académico TA137: transmisión de un archivo de texto, con los
apartados A/B implementados y contratos del apartado de modulación PAM/FSK.
Se procesa texto por caracteres, no por bytes
UTF-8. Cada símbolo es un punto de código Unicode de Python `str`.

## Arquitectura

```text
.txt UTF-8 → lectura → análisis de caracteres → Huffman → bits
→ conexión directa → decodificación Huffman → texto → escritura .txt UTF-8 → comparación
```

Ese es el flujo de la CLI actual. La función `run_modulation_simulation`
ya conecta las etapas del siguiente recorrido:

```text
bits Huffman → modulación → coordenadas → demodulación → bits sin relleno
→ decodificación Huffman → texto
```

La orquestación está implementada, pero sus dependencias de constelaciones,
recepción, mediciones y gráficos todavía lanzan `NotImplementedError`.
No se ocultan esas excepciones ni se simulan resultados faltantes. `main`
y la CLI conservan el flujo B. No se agrega ruido al canal.

Se conservan mayúsculas, acentos, espacios, controles, BOM y saltos CR/LF/CRLF.
No se normaliza Unicode: `é` y `e` seguido de acento combinante son secuencias
distintas. Un emoji compuesto puede contener varios puntos de código.
La representación como bytes solo aparece al leer/escribir el archivo UTF-8.

## Estructura

- `main.py`: lectura, rechazo controlado del vacío, transmisión de fuente,
  recepción directa, escritura, comparación y tablas del apartado B;
  `run_modulation_simulation` orquesta la etapa nueva como entrada separada.
- `config.py`: `SimulationConfig`, rutas de ejemplo en `res/`,
  `ModulationConfig` y `validate_modulation_config` implementado.
- `common/data_types.py`: dataclasses compartidas.
- `common/file_utils.py`: lectura/escritura UTF-8 y comparación textual exacta.
- `common/report_utils.py`: preparación y presentación de tablas y muestra
  de una línea para el informe, sin análisis ni conclusiones.
- `transmitter/source_analysis.py`: conteos, probabilidades y entropía.
- `transmitter/huffman.py`: árbol, código, estadísticas y eficiencia.
- `transmitter/source_encoder.py`: codificación por bloques de 65536 caracteres.
- `receiver/source_decoder.py`: reconstrucción de texto desde los bits.
- `transmitter/modulation.py`: PAM Gray existente y esqueleto de FSK ortogonal.
- `receiver/demodulation.py`: esqueletos del selector y receptores PAM/FSK.
- `common/constellations.py`: futura definición común de coordenadas y etiquetas.
- `common/modulation_metrics.py`: futuras energías, SER, BER e histograma.
- `common/modulation_plots.py`: futuros gráficos, sin importar Matplotlib todavía.
- `common/modulation_report.py`: presentación Markdown implementada, sin cálculos.
- `tests/`: pruebas automáticas; `pytest.ini` limita su recolección a esta carpeta.
- `experiments/`: scripts manuales; `test_B.py` conserva su estilo original,
  adaptado únicamente a claves de caracteres y resultado `str`.
- `requirements.txt`: pytest y NumPy, ya utilizado por el programa.
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

### Modulación y demodulación: PAM y FSK

- [x] PAM con Gray, coordenadas `(N, 1)` y metadato de relleno.
- [x] Contratos, dataclasses, docstrings y pruebas para las funciones pendientes.
- [x] Experimento manual PAM con entrada propia y sin ejecución al importarlo.
- [x] Validación de configuración, conectada al cargador y a la nueva simulación.
- [x] Presentación de energías, errores e histograma en Markdown.
- [x] Orquestación sin ruido, probada con sustitutos de las dependencias pendientes.
- [ ] Implementar la constelación compartida.
- [ ] Aplicar etiquetamiento configurable y tasa de canal en los moduladores.
- [ ] Modulación FSK y demodulación PAM/FSK.
- [ ] Energías teóricas/estimadas, SER, BER y frecuencias por símbolo.
- [ ] Gráficos con etiquetas y regiones e histograma.
- [ ] Completar las dependencias para ejecutar la simulación real de punta a punta.

### Otras etapas futuras

- [ ] Codificación y decodificación de canal.
- [ ] AWGN y respuesta impulsiva.

## Ejecución y tests

Requiere Python 3.10 o posterior. Ver [ENTORNO.md](ENTORNO.md).

```bash
python main.py
python -m pytest -q -rs
python -m experiments.test_B
python -m experiments.experimento_PAM
```

Si la entrada no existe, está vacía o no es UTF-8 válido, el principal
muestra un error y no escribe salida. No permite
que las rutas resueltas de entrada y salida sean iguales. La salida configurada
se sobrescribe cuando la ejecución es válida.

Las pruebas verifican contratos, Unicode, acentos, controles, bloques, errores,
ida y vuelta y E/S textual. Los experimentos manuales se documentan en
[experiments/README.md](experiments/README.md).

Los contratos, la validación, el informe, la orquestación con bloques
sustituidos y los casos de PAM existente se ejecutan. Los
casos funcionales de las funciones pendientes se omiten solo al recibir
`NotImplementedError` y quedan listos para ejecutarse al implementarlas.
Consultar [tests/README.md](tests/README.md) para distinguir ambos grupos.
Matplotlib queda como dependencia futura, cuando se implementen los gráficos.

## Contratos del apartado de modulación

`ModulationConfig(M, tipo, Eb=1.0, labeling="gray", code_rate=1.0)` agrega
metadatos para las implementaciones. El constructor no valida.
`validate_modulation_config` comprueba tipos, M en 2/4/8/16, esquema PAM/FSK,
etiquetas Gray/binarias, Eb finita positiva y tasa finita en (0, 1].
El cargador ya lo utiliza y rechaza M=1. No se aceptan booleanos como números.
PAM y el selector existentes todavía no aplican `labeling` ni `code_rate`.

Las coordenadas son matrices reales `(N, D)` en bases ortonormales: `D=1`
para PAM y `D=M` para FSK ortogonal coherente. `Constellation` asocia filas
con etiquetas; `ModulatedData` conserva `padding_bits`. `DemodulatedData`
conservará todos los símbolos decididos, pero devolverá los bits sin relleno.
Las decisiones empatadas elegirán la primera fila de la constelación.

`EnergyStatistics` distingue energía de símbolo, de bit de canal y de bit de
información. `ErrorRates` conserva SER y BER. `SymbolStatistics` incluye
conteos y probabilidades de todos los símbolos, incluso los no observados.
Estas dataclasses no calculan ni validan sus datos.

Las referencias teóricas supondrán símbolos equiprobables y AWGN; Eb/N0 se
expresará en dB respecto del bit de información. SER/BER serán anteriores a
decodificar el canal. Las muestras y comparaciones vacías o incompatibles se
rechazarán en las métricas. Los moduladores y demoduladores sí admitirán
secuencias vacías válidas. El histograma no demostrará automáticamente
equiprobabilidad; la interpretación y la explicación de Gray corresponden
al informe de los estudiantes.

Los README de [transmisor](transmitter/README.md), [receptor](receiver/README.md)
y [utilidades comunes](common/README.md) indican qué implementar en cada archivo.

## Uso de la orquestación de modulación

La llamada compatible con dos argumentos sigue disponible. El parámetro
opcional `eb_n0_db`, solo por nombre y por defecto 0 dB, identifica la referencia
teórica en AWGN; las muestras transmitidas siguen sin ruido.

```python
from config import load_config, load_modulation_config
from main import run_modulation_simulation

run_modulation_simulation(
    load_config(), load_modulation_config(4, "PAM"), eb_n0_db=0.0,
)
```

Con el estado actual esta llamada se detiene en `build_constellation`, que
sigue pendiente. La función conecta lectura, Huffman, modulación, demodulación,
energías, errores, histograma, informe, gráficos y recuperación de texto.
El receptor retira el relleno una sola vez. Se compara el archivo recibido
releído con la entrada y se presenta el resultado, sin usar el informe B.

Cuando los bloques estén implementados, se guardarán `<salida>.constellation.png`
y `<salida>.histogram.png` junto al archivo recibido; el directorio debe existir.
El Markdown se imprime por consola. Los errores de E/S se informan y las
dependencias pendientes propagan `NotImplementedError`.
Hasta integrar `labeling` y `code_rate` en los moduladores, esta entrada exige
Gray y tasa 1.0: otras opciones válidas se rechazan como todavía no implementadas.

## Funciones pendientes del apartado

- `common/constellations.py`: `build_constellation`.
- `transmitter/modulation.py`: `modulation_FSK`.
- `receiver/demodulation.py`: `demodulation`, `demodulation_PAM`, `demodulation_FSK`.
- `common/modulation_metrics.py`: `estimate_energies`, `theoretical_energies`,
  `estimate_symbol_error_rate`, `estimate_bit_error_rate`, `theoretical_error_rates`,
  `symbol_statistics`.
- `common/modulation_plots.py`: `plot_constellation`, `plot_symbol_histogram`.

Además, falta aplicar etiquetas configurables y tasa de canal en el selector
y los moduladores existentes, y compartir con ellos la definición de constelación.

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
