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
- `README.md`: documentación del transmisor.

Todos estos módulos están implementados y conectados al principal. No hacen
E/S ni normalizan texto. Las tablas del informe se preparan en common; las etapas de canal son posteriores.
El vector de palabras por carácter se obtiene con
`list(encoded.iter_codewords(huffman.codebook))`. Se materializa solo a pedido.
