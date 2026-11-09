# Receptor

- `__init__.py`: identifica el paquete.
- `source_decoder.py`: reconstruye `str` desde `EncodedSource` y un diccionario
  `dict[str, str]`. Construye un árbol y acumula caracteres, no bytes.
- `demodulation.py` contiene el selector `demodulation` y las decisiones
  PAM y FSK coherente.
- `README.md`: documentación y limitaciones.

La decodificación Huffman preserva acentos, controles y puntos de código.
Rechaza bits inválidos, palabras de código duplicadas y recorridos incompatibles
con el árbol. `discard_incomplete=True` descarta una palabra final incompleta.
Con `discard_incomplete=False`, esa palabra produce `ValueError`.

Requiere un código prefijo válido con palabras binarias no vacías. Sigue
pendiente validar por completo el diccionario: caracteres de código inválidos,
palabras vacías y conflictos de prefijos en ambos órdenes de inserción.
La escritura y la comparación se realizan en `common/file_utils.py`.

## Demodulación

`demodulation(modulated, config)` recibe las coordenadas observadas y usa la
misma constelación y el mismo etiquetado que el transmisor. Decide el símbolo
de menor distancia. Las coordenadas de PAM tienen dimensión `(N, 1)` y las
de FSK ortogonal `(N, M)`. En caso de empate elige la primera fila de la
constelación.

`DemodulatedData` contiene las coordenadas decididas y la cadena de etiquetas
binarias. Los bits de un grupo incompleto ya fueron descartados en transmisión.
La SER compara las coordenadas decididas con las transmitidas. La BER compara
los bits recuperados con la secuencia original antes de decodificar Huffman.
