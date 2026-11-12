# Transmisor

- `__init__.py`: identifica el paquete.
- `source_analysis.py`: `analyze_source(str)` cuenta puntos de código Unicode y
  calcula probabilidades. `calculate_entropy` omite ceros y rechaza negativos.
- `huffman.py`: recibe `dict[str, float]` y devuelve códigos `dict[str, str]`.
  Conserva el algoritmo de árbol. Calcula H(X) como mínimo promedio teórico,
  promedio real, varianza, propiedad de prefijo y eficiencia. Rechaza fuente
  vacía; un único carácter recibe "0".
- `source_encoder.py`: codifica bloques de 65536 caracteres, preservando orden.
  Devuelve bits vacíos para texto vacío y rechaza caracteres sin código.
  La lista temporal está acotada, pero la salida completa sigue en memoria.
- `modulation.py` contiene el selector `modulation` y los moduladores PAM y FSK.
- `README.md`: documentación del transmisor.

Los módulos de fuente están implementados y conectados al principal. No hacen
E/S ni normalizan texto. Las tablas del informe se preparan en common.
La modulación se usa en `main.run_modulation_simulation` y en los experimentos.
El vector de palabras por carácter se obtiene con
`list(encoded.iter_codewords(huffman.codebook))`. Se materializa solo a pedido.

## Modulación

`modulation_PAM(encoded, config)` y `modulation_FSK(encoded, config)` reciben
`EncodedSource` y `ModulationConfig`. Usan `build_constellation` para obtener
coordenadas y etiquetas. Gray reflejado es el valor por defecto y el binario
natural se elige con `labeling="binary"`.

El transmisor agrupa `log2(M)` bits por símbolo. Si el último grupo queda
incompleto, descarta esos bits y marca `ModulatedData.flag_descarte`. Para
bloques completos, `ModulatedData.symbols` contiene coordenadas `(N, 1)` para
PAM o `(N, M)` para FSK ortogonal. La energía de referencia de la constelación
es `Es = log2(M) · Eb · code_rate` con símbolos equiprobables.

Los flujos con métricas requieren al menos un grupo completo. El orquestador
`main.run_modulation_simulation` admite Gray y tasa 1.

## Codificación de canal

`channel_encoder.py` declara dos funciones con implementación pendiente:

- `encode_channel_word(message_bits: str, code: ChannelCodeConfig) -> str`
  recibe un mensaje de `k` bits y devuelve una palabra de `n` bits, con el
  mensaje en los últimos `k` bits.
- `encode_channel(source: EncodedSource, code: ChannelCodeConfig) -> EncodedChannel`
  agrupa los bits Huffman en bloques de `k` y usa `encode_channel_word` para
  cada bloque. Completa el último con ceros a la derecha si hace falta y
  devuelve las palabras concatenadas junto con la longitud original en
  `source_bit_length`. La fuente vacía corresponde a un flujo de longitud cero.
