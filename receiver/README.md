# Receptor

- `__init__.py`: identifica el paquete.
- `source_decoder.py`: reconstruye `str` desde `EncodedSource` y un diccionario
  `dict[str, str]`. Construye un árbol y acumula caracteres, no bytes.
- `demodulation.py`: esqueletos `demodulation`, `demodulation_PAM` y
  `demodulation_FSK`; todos lanzan `NotImplementedError`.
- `README.md`: documentación y limitaciones.

La decodificación está implementada y conectada al principal. Preserva acentos,
controles y puntos de código sin normalizarlos. Rechaza bits de entrada
inválidos, palabras duplicadas, recorridos incompatibles y palabras incompletas.

Requiere un código prefijo válido con palabras binarias no vacías. Sigue
pendiente validar por completo el diccionario: caracteres de código inválidos,
palabras vacías y conflictos de prefijos en ambos órdenes de inserción.
La migración textual no modifica esa lógica. Escritura y comparación se hacen
en `common/file_utils.py`; demodulación y decodificación de canal son futuras.

## Demodulación: trabajo pendiente

En `demodulation` implementar la selección PAM/FSK, usando `ModulatedData` y
`ModulationConfig`. En las funciones específicas implementar las decisiones
sobre la constelación común y recuperar sus etiquetas, con recepción coherente
para FSK ortogonal. Las dimensiones serán `(N, 1)` para PAM y `(N, M)` para FSK.
Si hay empate, elegir la primera fila de la constelación.

Devolver `DemodulatedData`: coordenadas decididas de los N símbolos y cadena
de bits con el relleno final retirado una sola vez. Conservar el último
símbolo para medir SER, aunque contuviera relleno. Una entrada vacía válida
devolverá coordenadas `(0, D)` y bits vacíos. Rechazar dimensiones, coordenadas
no finitas, configuración o cantidad de relleno incompatibles.

No decodificar Huffman dentro de este módulo. Su salida binaria se conectará
al decodificador de fuente desde el futuro principal. Los casos conocidos,
empates, etiquetas, relleno e ida y vuelta están en `tests/test_demodulation.py`
y se omiten solo mientras las funciones lancen `NotImplementedError`.
