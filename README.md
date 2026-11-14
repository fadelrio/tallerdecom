# Sistema de comunicaciones digitales

Proyecto académico TA137. Incluye el recorrido de fuente de los apartados A/B
y la modulación, demodulación y obtención de datos para los apartados D/E.
El análisis de fuente usa puntos de código Unicode de Python `str`.

## Arquitectura

```text
.txt UTF-8 → lectura → análisis de caracteres → Huffman → bits
→ conexión directa → decodificación Huffman → texto → escritura .txt UTF-8 → comparación
```

Ese es el flujo de la CLI actual. La función `run_modulation_simulation`
ya conecta las etapas del siguiente recorrido:

```text
bits Huffman → modulación → coordenadas → demodulación → bits recuperados
→ decodificación Huffman → texto
```

`main` y la CLI ejecutan el flujo B. El orquestador de modulación mide energías,
errores y frecuencias de símbolos. El canal AWGN se usa en los experimentos.

La lectura y la escritura conservan mayúsculas, acentos, espacios, controles,
BOM y saltos CR/LF/CRLF.
No se normaliza Unicode: `é` y `e` seguido de acento combinante son secuencias
distintas. Un emoji compuesto puede contener varios puntos de código.
La representación como bytes solo aparece al leer/escribir el archivo UTF-8.

## Estructura

- `main.py`: lectura, rechazo controlado del vacío, transmisión de fuente,
  recepción directa, escritura, comparación y tablas del apartado B;
  `run_modulation_simulation` orquesta la etapa nueva como entrada separada.
- `config.py` define las rutas de fuente, los parámetros de modulación y el
  cálculo de `N0` a partir de `Eb/N0`.
- `channel/channel.py` aplica ruido AWGN a las coordenadas moduladas.
- `common/data_types.py`: dataclasses compartidas.
- `common/file_utils.py`: lectura/escritura UTF-8 y comparación textual exacta.
- `common/report_utils.py` prepara las tablas y la muestra de texto del apartado B.
- `transmitter/source_analysis.py`: conteos, probabilidades y entropía.
- `transmitter/huffman.py`: árbol, código, estadísticas y eficiencia.
- `transmitter/source_encoder.py`: codificación por bloques de 65536 caracteres.
- `receiver/source_decoder.py`: reconstrucción de texto desde los bits.
- `transmitter/modulation.py`: moduladores PAM y FSK ortogonal.
- `receiver/demodulation.py`: decisiones PAM y FSK por distancia mínima.
- `common/constellations.py`: definición común de coordenadas y etiquetas.
- `common/modulation_metrics.py` calcula energías, tasas de error y frecuencias
  por símbolo.
- `common/modulation_plots.py` genera constelaciones e histogramas en PNG.
- `common/modulation_report.py`: presentación Markdown implementada, sin cálculos.
- `tests/`: pruebas automáticas; `pytest.ini` limita su recolección a esta carpeta.
- `experiments/` contiene los scripts exploratorios y el generador de datos de D/E.
- `requirements.txt`: pytest, NumPy y Matplotlib.
- `ENTORNO.md`: preparación del entorno sin depender de ningún editor o agente.
- Los `__init__.py` identifican paquetes; cada paquete tiene su propio README.

## Contratos de fuente

`read_file(Path) -> str`, `analyze_source(str) -> SourceStatistics`,
`build_huffman_code(dict[str, float]) -> HuffmanResult`,
`encode_source(str, dict[str, str]) -> EncodedSource`,
`decode_source(EncodedSource, dict[str, str], discard_incomplete=True) -> str`,
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

- [x] Modulación y demodulación PAM/FSK para grupos completos de bits.
- [x] Experimentos de modulación, BER y energía media.
- [x] Validación de configuración, conectada al cargador y a la nueva simulación.
- [x] Presentación de energías, errores e histograma en Markdown.
- [x] Orquestación sin ruido con pruebas de recuperación de texto.
- [x] Constelación compartida con etiquetado configurable y ajuste de energía por tasa.
- [x] SER y BER teóricas en AWGN y gráfico con etiquetas y regiones de decisión.
- [x] BER medida con conteos de bits errados, incluyendo los descartados al modular.
- [x] Energías teóricas y estimadas, frecuencias por símbolo e histograma.
- [x] Datos de D y E, con una corrida reproducible de AWGN a 6 dB.
- [ ] Corregir `Eb` estimada para tasas de código menores que 1.

### Otras etapas futuras

- [x] Contratos de codificación y decodificación de canal del apartado C.
- [ ] Implementación e integración de la codificación y decodificación de canal.
- [ ] Análisis de desempeño con el barrido del apartado F.

## Contratos del apartado de codificación de canal

El apartado C tiene las interfaces definidas y la implementación pendiente.
Los bloques se ubicarán en este recorrido:

```text
Huffman → codificación de canal → modulación → canal → demodulación
→ decodificación de canal → decodificación Huffman
```

`config.GROUP_4_CHANNEL_CODE` contiene los parámetros y la matriz generadora
asignados al grupo 4. El código sistemático (10, 4) tiene tasa 0.4, distancia
mínima 3 y corrección garantizada de un error por palabra. La macro booleana
`CHANNEL_CODING_ENABLED` en `main.py` activa o desactiva conjuntamente el
codificador y el decodificador de canal; usa `code_rate=0.4` activada y
`code_rate=1.0` desactivada. Los contratos se documentan en los README de
[transmisor](transmitter/README.md), [receptor](receiver/README.md) y
[utilidades comunes](common/README.md).

La integración también deberá agregar y retirar el relleno propio de la
modulación por separado del relleno de canal. Con M=8, el modulador actual
agrupa de a tres bits y el descarte del sobrante puede dejar incompleta la
última palabra de canal.

## Ejecución y tests

Requiere Python 3.10 o posterior. Ver [ENTORNO.md](ENTORNO.md).

```bash
python main.py
python -m experiments.modulation_data
python -m pytest -q
```

Si la entrada no existe, está vacía o no es UTF-8 válido, el principal
muestra un error y no escribe salida. No permite
que las rutas resueltas de entrada y salida sean iguales. La salida configurada
se sobrescribe cuando la ejecución es válida.

Las pruebas verifican contratos, Unicode, acentos, controles, bloques, errores,
ida y vuelta y E/S textual. Los experimentos manuales se documentan en
[experiments/README.md](experiments/README.md).

Consultar el [estado de la suite](tests/README.md) para ver los fallos conocidos
y la selección de pruebas de métricas, gráficos y orquestación.

## Contratos del apartado de modulación

`ModulationConfig(M, tipo, Eb=1.0, labeling="gray", code_rate=1.0)` agrega
metadatos para las implementaciones. El constructor no valida.
`validate_modulation_config` comprueba tipos, M en 2/4/8/16, esquema PAM/FSK,
etiquetas Gray/binarias, Eb finita positiva y tasa finita en (0, 1].
El cargador ya lo utiliza y rechaza M=1. No se aceptan booleanos como números.
PAM y FSK usan Gray por defecto y admiten `labeling="binary"`.

Las coordenadas son matrices reales `(N, D)` en bases ortonormales: `D=1`
para PAM y `D=M` para FSK ortogonal coherente. `Constellation` asocia filas
con etiquetas. El modulador indica el descarte de bits con `flag_descarte`.
El demodulador devuelve los símbolos decididos y sus bits.
La BER medida cuenta como error cada bit sin contraparte y usa como denominador
la longitud de la secuencia más larga. El informe muestra la tasa y los conteos.
Las decisiones empatadas eligen la primera fila de la constelación.

`EnergyStatistics` distingue energía de símbolo, de bit de canal y de bit de
información. `ErrorRates` conserva SER y BER. `SymbolStatistics` incluye
conteos y probabilidades de todos los símbolos, incluso los no observados.
Estas dataclasses no calculan ni validan sus datos.

Las referencias teóricas suponen símbolos equiprobables y AWGN. `Eb/N0` se
expresa en dB respecto del bit de información. La SER y la BER se miden sobre
las decisiones del demodulador. Las métricas requieren muestras no vacías y
entradas compatibles. El histograma incluye la referencia equiprobable `1/M`
para comparar con las frecuencias observadas.

Los README de [transmisor](transmitter/README.md), [receptor](receiver/README.md)
y [utilidades comunes](common/README.md) detallan las interfaces y sus limitaciones.

## Constelaciones y referencia en AWGN

```python
from pathlib import Path

from common.constellations import build_constellation
from common.modulation_metrics import theoretical_error_rates
from common.modulation_plots import plot_constellation
from config import ModulationConfig

config = ModulationConfig(4, "FSK")
constellation = build_constellation(config)
plot_constellation(constellation, Path("constelacion.png"))
rates = [theoretical_error_rates(config, db) for db in range(11)]
```

`plot_constellation` admite `received_symbols` para superponer las muestras
del canal. En FSK de más de dos dimensiones, el gráfico muestra las regiones
en un corte ortonormal por el origen y proyecta las muestras en ese plano.

## Datos para los apartados D y E

Ejecutar desde la raíz con las dependencias de `requirements.txt` instaladas.

```bash
python -m experiments.modulation_data
```

Genera [el Markdown de datos](res/modulation_info.md) y sus tres PNG en `res/`.
La tabla cubre PAM y FSK con M = 2, 4, 8 y 16. Para los gráficos y la corrida
con AWGN a 6 dB se usa 4-PAM Gray sobre `res/textito.txt`, con semilla 42.
Esta corrida usa tasa 1. Se puede cambiar la muestra con `--input`, `--tipo`
y `--orden`, y el destino del Markdown y sus PNG con `--output`.

## Uso de la orquestación de modulación

La llamada compatible con dos argumentos sigue disponible. El parámetro
opcional `eb_n0_db`, solo por nombre y por defecto 0 dB, identifica la referencia
teórica en AWGN; las muestras transmitidas siguen sin ruido.

```python
from pathlib import Path

from config import SimulationConfig, load_modulation_config
from main import run_modulation_simulation

run_modulation_simulation(
    SimulationConfig(Path("res/textito.txt"), Path("recibido_modulacion.txt")),
    load_modulation_config(4, "PAM"), eb_n0_db=0.0,
)
```

Se guardan `<salida>.constellation.png` y `<salida>.histogram.png` junto al
archivo recibido. El directorio debe existir. El Markdown se imprime por
consola y se informan los errores de E/S.
Esta entrada admite Gray y tasa 1.0.

## Mantenimiento

Actualizar código, pruebas, docstrings y README juntos. No marcar como
implementadas interfaces que solo lanzan `NotImplementedError`.

## Datos para el informe B

`python main.py` usa `res/muchos_martin_fierro.txt` como entrada y sobrescribe
`res/output.txt` con el texto recibido. También se puede elegir cada ruta por
terminal. La salida de datos se organiza en seis secciones.

1. Carácter escapado, identificador Unicode, cantidad, probabilidad, código y longitud.
2. Verificación de prefijo por pares, indicador del constructor, alfabeto y longitudes.
3. Entropía, mínimo promedio teórico, promedio real, varianza, eficiencia y código fijo.
4. Totales de bits Huffman y referencia fija (sin diccionario ni metadatos).
5. Muestra de las líneas 127 y 128, palabras binarias por carácter, bits
   concatenados y texto decodificado, con los controles escapados.
6. Igualdad de los textos y cantidades de caracteres, tras releer el archivo recibido.

La muestra requiere al menos 128 líneas según `str.splitlines()`. Con un texto
más corto, el programa escribe el archivo recibido y luego falla con `IndexError`
al preparar el Markdown. El título de la muestra conserva el rótulo «Primera
línea» y el campo «En archivo recibido» muestra el prefijo del archivo.
[Salida guardada de una corrida anterior](res/output_info.md).

Para guardar el Markdown en un archivo independiente, redirigir la salida.

```bash
python main.py > datos_informe.md
```

Usar un destino distinto de la entrada y del archivo recibido.

## Usar textos propios o descargados de Gutenberg

La CLI admite archivos locales UTF-8. Para generar el Markdown de B, elegir un
texto de al menos 128 líneas. Las rutas de ejemplo se pasan por terminal.

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

En el apartado B, `main.py` imprime las tablas en Markdown por consola y
escribe el texto recibido en `--output`. Los símbolos especiales se escapan en
las tablas y la muestra se incluye en un bloque literal.

```bash
# Ver el Markdown por consola
python main.py --input "mi_texto.txt" --output "recibido.txt"

# Guardar la salida cuando se desee
python main.py --input "mi_texto.txt" --output "recibido.txt" > informe.md
```

La redirección la realiza la terminal. `informe.md` debe ser distinto tanto del
archivo de entrada como del archivo recibido, porque `>` abre el destino antes
de que comience el programa.
