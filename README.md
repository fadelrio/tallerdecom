# Sistema de comunicaciones digitales

Proyecto académico en Python para simular un sistema de comunicaciones
digitales. Esta primera etapa contiene exclusivamente la arquitectura de los
apartados **A (datos, control y estructura general)** y **B (fuente y Huffman)**.
Están implementados el análisis de fuente, la entropía, Huffman y sus
estadísticas, la eficiencia y la codificación por bloques. La decodificación,
la escritura, la comparación y los datos del informe siguen pendientes.
La lectura binaria y el transmisor están conectados al principal.

## Arquitectura

```text
Fuente → Transmisor → Canal → Receptor → Archivo recibido

Configuración
  → Lectura binaria
  → Análisis estadístico y entropía
  → Construcción de Huffman y estadísticas del código
  → Eficiencia
  → Codificación de fuente
  → [Futuro: codificación de canal y modulación]
  → [Futuro: AWGN y respuesta impulsiva]
  → [Futuro: demodulación y decodificación de canal]
  → Decodificación de fuente
  → Escritura binaria
  → Comparación con el original
  → Preparación de datos del informe B
```

`main.py` carga la configuración y lee el archivo en modo binario. Si existe
y no está vacío, ejecuta análisis, Huffman, eficiencia y codificación. Si no
existe, muestra el recorrido conceptual. No llama a placeholders.
`[PENDIENTE]` identifica funcionalidades de A/B; `[NO IMPLEMENTADO]` identifica
etapas futuras, para las cuales todavía no existen módulos.

Las interfaces pendientes lanzan `NotImplementedError` si se invocan
directamente. Así se evita confundir un resultado ficticio con una operación
implementada. Al implementar cada módulo se conectará su interfaz en el
orquestador y se actualizará ese contrato.

La fuente se representa como `bytes`: cada símbolo es un entero entre 0 y 255,
incluidos controles y bytes no imprimibles. La futura E/S será binaria.
No se decodifica texto. La presentación legible será una responsabilidad
separada y no alterará los símbolos. Los bits Huffman se representarán como
una cadena de `'0'` y `'1'` para facilitar su inspección académica.

## Estructura del proyecto

La carpeta actual es la raíz del proyecto (equivale a `proyecto/` en la consigna).

```text
proyecto/
├── main.py                       # Orquestación conceptual y estados
├── config.py                     # SimulationConfig y rutas de ejemplo
├── README.md                     # Documentación y estado real
├── ENTORNO.md                    # Instalación del venv para colaboradores
├── requirements.txt              # Dependencia de pruebas
├── .gitignore                    # Cachés y entorno virtual local
├── transmitter/
│   ├── README.md                  # Responsabilidades y tareas pendientes
│   ├── __init__.py                # Paquete del transmisor
│   ├── source_analysis.py         # Análisis estadístico y entropía
│   ├── huffman.py                 # Huffman, estadísticas y eficiencia
│   └── source_encoder.py          # Codificación de fuente por bloques
├── receiver/
│   ├── README.md                  # Responsabilidades y tareas pendientes
│   ├── __init__.py                # Paquete del receptor
│   └── source_decoder.py          # Contrato de decodificación de fuente
├── common/
│   ├── README.md                  # Responsabilidades y tareas pendientes
│   ├── __init__.py                # Paquete compartido
│   ├── data_types.py              # Dataclasses sin cálculos
│   ├── file_utils.py              # Contratos de E/S y comparación
│   └── report_utils.py            # Contratos de datos del informe
└── tests/
    ├── README.md                  # Cobertura actual y ampliaciones futuras
    ├── __init__.py                # Paquete de pruebas
    ├── test_source.py             # Imports, contratos y ejecución
    ├── test_main.py               # Lectura y rechazo controlado
    └── test_transmitter.py        # Codificación e integración de fuente
```

Las estructuras compartidas no dependen del transmisor ni del receptor.
Las utilidades de archivos no conocen Huffman. El módulo de informes prepara
datos científicos para una futura presentación, sin generar PDF ni Word.
No se introducen dependencias circulares.

Cada paquete tiene una guía de sus archivos y del trabajo por implementar:
[common](common/README.md), [transmitter](transmitter/README.md),
[receiver](receiver/README.md) y [tests](tests/README.md).

## Interfaces y estructuras

| Módulo | Interfaces públicas |
| --- | --- |
| `main` | `main() -> None` |
| `config` | `SimulationConfig`, `load_config() -> SimulationConfig` |
| `transmitter.source_analysis` | `analyze_source(data) -> SourceStatistics`, `calculate_entropy(probabilities) -> float` |
| `transmitter.huffman` | `build_huffman_code(probabilities) -> HuffmanResult`, `calculate_efficiency(entropy, average_length) -> float` |
| `transmitter.source_encoder` | `encode_source(data, codebook) -> EncodedSource` |
| `receiver.source_decoder` | `decode_source(encoded, codebook) -> bytes` |
| `common.file_utils` | `read_file(path) -> bytes`, `write_file(path, data) -> None`, `compare_data(original, received) -> FileComparison` |
| `common.report_utils` | `build_source_table(statistics, huffman) -> list[SourceReport]`, `build_coding_report(statistics, huffman, encoded) -> CodingReport` |

`common.data_types` define:

- `SourceStatistics`: conteos, probabilidades, total de símbolos y entropía.
- `CodeStatistics`: longitud mínima, promedio, varianza y propiedad de prefijo.
- `HuffmanResult`: diccionario del código y sus estadísticas.
- `EncodedSource`: cadena de bits.
- `FileComparison`: igualdad y tamaños en bytes.
- `SourceReport`: símbolo entero, cantidad, probabilidad y palabra Huffman.
- `CodingReport`: entropía, longitudes, varianza, eficiencia, longitud fija
  y totales de bits Huffman y fijo.

Las dataclasses solo almacenan datos; no calculan ni validan sus atributos.
La eficiencia se calcula como `H(X) / L_promedio`, una fracción adimensional.
La referencia fija será de **8 bits por símbolo**. La conversión de eficiencia
a porcentaje pertenecerá a la presentación. El análisis admite fuente vacía y símbolo único. Huffman rechaza el
diccionario vacío y asigna "0" al símbolo único. El principal rechaza archivos vacíos con un mensaje antes de Huffman; ver el
[README del transmisor](transmitter/README.md).

## Estado del proyecto

### Apartado A

- [x] Estructura general
- [x] Configuración de ejemplo
- [x] Programa principal con recorrido conceptual
- [x] Arquitectura modular
- [x] Lectura binaria del archivo
- [x] Conexión del transmisor al orquestador
- [ ] Conexión del receptor, escritura, comparación e informe

### Apartado B

- [x] Análisis estadístico y probabilidades
- [x] Entropía
- [x] Huffman
- [x] Longitud mínima
- [x] Longitud promedio
- [x] Varianza
- [x] Verificación de código prefijo
- [x] Eficiencia
- [x] Codificación de fuente por bloques
- [ ] Decodificación
- [ ] Generación del archivo recibido
- [ ] Comparación con el original
- [ ] Datos para el informe y comparación con código fijo de 8 bits

### Etapas futuras

- [ ] Codificación de canal
- [ ] Modulación
- [ ] Canal AWGN
- [ ] Respuesta impulsiva
- [ ] Demodulación
- [ ] Decodificación de canal

Las marcas indican que existe implementación, no una validación exhaustiva.
Quedan pendientes las funcionalidades no marcadas. La suite da
**59 aprobadas y 3 omitidas**, estas últimas por el decodificador pendiente.
Ver [detalles de pruebas](tests/README.md).

## Ejecución

Se requiere Python **3.10 o posterior** (compatible con las anotaciones usadas
y la dependencia de pruebas). Desde la raíz del proyecto:

```bash
python3 main.py
```

No es necesario instalar dependencias para ejecutar el programa principal.
Sin archivo se muestra el recorrido conceptual. Con un archivo no vacío se
lee y codifica la fuente; todavía no se escribe un archivo recibido. Una
entrada vacía se rechaza sin traceback y sin modificar la salida.
`load_config()` devuelve las rutas `entrada.bin` y `recibido.bin` junto a
`config.py`, independientemente del directorio desde el cual se ejecute.
Estas rutas de ejemplo pueden editarse en `config.py`.

## Dependencias y tests

Consultar [Preparación del entorno para colaboradores](ENTORNO.md) para crear
el entorno en Linux, macOS o Windows, configurar el editor y resolver problemas
como `No module named pip`. La guía no requiere Codex.

El código del sistema usa exclusivamente la biblioteca estándar de Python.
`pytest` es la única dependencia externa y se utiliza para pruebas. No se
utiliza NumPy.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest
```

Las pruebas verifican imports, instanciación y documentación de dataclasses,
firmas y anotaciones de funciones, la excepción explícita de los placeholders,
la configuración y la ejecución de `main.py` en un proceso independiente.
Se usan datos manuales de ejemplo, incluidos símbolos 0 y 255. Las pruebas
del codificador ya verifican su comportamiento real; las integraciones con
análisis, Huffman y decodificación se omiten mientras estén pendientes.
Al implementar cada interfaz se deben reemplazar sus pruebas de
`NotImplementedError` por pruebas de comportamiento real y casos límite.

## Relación con la consigna

- **A:** `config.py` define datos de control; `main.py` muestra el flujo;
  los paquetes separan las responsabilidades; `file_utils.py` define las
  interfaces para lectura, escritura y comparación binarias.
- **B:** `source_analysis.py` define análisis y entropía; `huffman.py` define
  construcción y estadísticas; `source_encoder.py` y `source_decoder.py`
  definen la transformación reversible futura. `data_types.py` establece
  los resultados compartidos y `report_utils.py` las tablas y métricas
  requeridas para el informe.

## Mantenimiento del README

Cada implementación posterior debe actualizar su estado aquí, ajustar la
arquitectura y estructura si cambian, revisar las instrucciones de ejecución
y actualizar o documentar las pruebas correspondientes. También debe conectar
la etapa en `main.py` cuando sus dependencias estén disponibles. Una interfaz
que solo contiene un placeholder debe seguir marcada como pendiente.

## Codificación por bloques y pruebas de integración

`encode_source` procesa bloques de 64 KiB, concatena las palabras de cada
bloque y finalmente une los fragmentos. Devuelve una cadena vacía para una
fuente vacía y lanza `ValueError` si un byte no tiene código. Asume palabras
binarias no vacías y un código prefijo válido provisto por Huffman.

La lista temporal está acotada por bloque, pero la entrada y toda la salida
siguen en memoria; los fragmentos y la cadena final pueden coexistir. No es
streaming ni almacenamiento de bits empaquetados. No se realizaron benchmarks
de tiempo o memoria.

`tests/test_transmitter.py` prueba resultados conocidos, símbolos 0..255,
entrada vacía, límites de bloque y símbolos sin código. Incluye pruebas de
análisis con código manual, ida y vuelta con código manual, transmisor completo
y recorrido completo de fuente. Las llamadas a módulos todavía pendientes se
omiten con `pytest.skip` solo si lanzan `NotImplementedError`; los demás errores
fallan normalmente. Al implementar esos módulos, sus pruebas se ejecutarán
sin modificar la selección. Ejecutar `python -m pytest -q -rs` para ver motivos
de omisión. Una prueba omitida no cuenta como funcionalidad verificada.
