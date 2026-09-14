# Transmisor: análisis y codificación de fuente

Este paquete contiene las interfaces del apartado B anteriores a la transmisión.
Actualmente todas sus funciones son placeholders que lanzan
`NotImplementedError`; no hay algoritmos implementados.

## Archivos y trabajo pendiente

| Archivo | Responsabilidad actual | Qué implementar posteriormente |
| --- | --- | --- |
| `__init__.py` | Identifica y documenta el paquete del transmisor. | No requiere lógica adicional; mantenerlo sin efectos secundarios al importar. |
| `source_analysis.py` | Declara `analyze_source(data: bytes) -> SourceStatistics`. | Recorrer los bytes, contar símbolos, calcular probabilidades y entropía y devolver las estadísticas. |
| `huffman.py` | Declara `build_huffman_code` y `calculate_efficiency`. | Construir el árbol y las palabras Huffman, obtener estadísticas y verificar la propiedad de prefijo; calcular la eficiencia. |
| `source_encoder.py` | Declara `encode_source(data, codebook) -> EncodedSource`. | Sustituir cada byte por su palabra Huffman y concatenar las palabras en el orden original. |
| `README.md` | Describe responsabilidades y pendientes del paquete. | Actualizarlo junto con cada implementación. |

## Contratos que debe respetar la implementación

`analyze_source` recibe bytes, incluidos controles y valores no imprimibles.
Los conteos y probabilidades usan símbolos enteros `0..255`. La entropía se
expresa en bits por símbolo.

`build_huffman_code` recibe el diccionario de probabilidades y devuelve un
`HuffmanResult` con el código y sus `CodeStatistics`: longitud mínima,
longitud promedio y varianza ponderadas por probabilidad, y verificación de
código prefijo. El cálculo de estas estadísticas pertenece a esta función.
`calculate_efficiency` devolverá `H(X) / L_promedio` como fracción adimensional.

`encode_source` devuelve `EncodedSource.bits` como una cadena de `'0'` y `'1'`.
No debe leer archivos, convertir la fuente a texto ni generar señales.

Antes de implementar, definir y probar el comportamiento para fuente vacía,
símbolo único y entradas inválidas. Todavía no se fija una política para ellos.

## Integración futura

El orquestador conectará análisis → Huffman → codificación utilizando las
estructuras de [`common`](../common/README.md). La lectura corresponde a las
utilidades de archivos y la preparación del informe a `common/report_utils.py`.
La codificación de canal y la modulación son etapas posteriores sin módulos
en esta versión.

Al implementar, reemplazar las pruebas del placeholder correspondiente por
pruebas funcionales y actualizar este documento y el [README general](../README.md).
