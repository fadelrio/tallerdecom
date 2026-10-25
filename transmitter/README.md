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
- `modulation.py`: contiene el selector `modulation`, el modulador
  `modulation_PAM` existente y el esqueleto `modulation_FSK`.
- `README.md`: documentación del transmisor.

Los módulos de fuente están implementados y conectados al principal. No hacen
E/S ni normalizan texto. Las tablas del informe se preparan en common.
La modulación se usa desde el experimento PAM, todavía no desde el principal.
El vector de palabras por carácter se obtiene con
`list(encoded.iter_codewords(huffman.codebook))`. Se materializa solo a pedido.

## Modulación: estado y trabajo pendiente

PAM conserva íntegra su lógica actual: bits en `EncodedSource`, Gray reflejado,
relleno con ceros, coordenadas `(N, 1)` y energía de bit del flujo de entrada.
El selector solo distingue PAM y FSK; FSK lanza `NotImplementedError`.

En `modulation_FSK` implementar el agrupamiento de bits, el relleno y las
coordenadas `(N, M)` de FSK ortogonal. La firma actual mantiene `encoded, M, Eb`;
el caso básico tendrá Gray reflejado por orden de eje, igual que la futura
constelación común con valores por defecto. La entrada vacía devolverá una
matriz `(0, M)` sin relleno. No generar formas de onda.

Queda pendiente conectar el selector y los moduladores con
`common.constellations.build_constellation` y con el validador ya implementado
`config.validate_modulation_config`, aplicar `labeling` y `code_rate`, y
rechazar esquemas desconocidos explícitamente. No se ha implementado esa
integración ni se ha cambiado la lógica PAM para hacerla. La entrada
`main.run_modulation_simulation` valida antes de transmitir y rechaza por ahora
etiquetas binarias o tasas distintas de 1.0, para evitar que se ignoren.

Los casos de PAM existente se ejecutan en `tests/test_modulation.py`; los de
FSK y constelaciones quedan preparados y se omiten mientras estén pendientes.
