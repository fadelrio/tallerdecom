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

## Decodificación de canal

`channel_decoder.py` declara dos funciones con implementación pendiente:

- `decode_channel_word(received_word: str, parity_check_matrix: np.ndarray, syndrome_table: SyndromeTable) -> ChannelWordDecoding`
  recibe una palabra de `n` bits y devuelve la palabra resultante, el
  síndrome de la palabra recibida y la máscara aplicada.
- `decode_channel(received_bits: str, parity_check_matrix: np.ndarray, syndrome_table: SyndromeTable, *, source_bit_length: int) -> DecodedChannel`
  recibe el flujo demodulado sin relleno de modulación. Procesa palabras de
  `n` bits, concatena los últimos `k` bits de cada resultado y recorta el
  relleno de canal según la longitud original. Devuelve un `EncodedSource`
  y los conteos de bloques con síndrome distinto de cero y de bloques
  detectados que quedaron sin corregir.

Para un síndrome cero se registra una máscara de ceros. Si se detecta un error
y se conserva la palabra recibida, la máscara vale `None`. La política para
líderes de peso dos o más queda pendiente.
