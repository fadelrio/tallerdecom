# Transmisor: análisis y codificación de fuente

Este paquete contiene las interfaces del apartado B anteriores a la transmisión.
Están implementados análisis, entropía, construcción de Huffman, estadísticas,
eficiencia y codificación por bloques. Están conectados al programa principal para archivos no vacíos.
Queda por ampliar la validación de casos límite.

## Archivos y trabajo pendiente

| Archivo | Responsabilidad actual | Qué implementar posteriormente |
| --- | --- | --- |
| `__init__.py` | Identifica y documenta el paquete del transmisor. | No requiere lógica adicional; mantenerlo sin efectos secundarios al importar. |
| `source_analysis.py` | Implementa `analyze_source` y `calculate_entropy`. | Ampliar las pruebas de casos límite; los ceros se omiten y los negativos se rechazan. |
| `huffman.py` | Implementa `build_huffman_code` y `calculate_efficiency`. | Ampliar validaciones de entrada; se mantiene el rechazo del diccionario vacío. |
| `source_encoder.py` | Implementa `encode_source(data, codebook) -> EncodedSource` por bloques de 64 KiB. | Integrarla con el receptor cuando esté disponible. |
| `README.md` | Describe responsabilidades y pendientes del paquete. | Actualizarlo junto con cada implementación. |

## Contratos que debe respetar la implementación

`analyze_source` recibe bytes, incluidos controles y valores no imprimibles.
Los conteos y probabilidades usan símbolos enteros `0..255`. La entropía se
expresa en bits por símbolo.

`build_huffman_code` recibe el diccionario de probabilidades y devuelve un
`HuffmanResult` con el código y sus `CodeStatistics`: largo promedio mínimo teórico H(X),
longitud promedio y varianza ponderadas por probabilidad, y verificación de
código prefijo. El cálculo de estas estadísticas pertenece a esta función.
`calculate_efficiency` devuelve `H(X) / L_promedio` como fracción adimensional.

`encode_source` devuelve `EncodedSource.bits` como una cadena de `'0'` y `'1'`.
No debe leer archivos, convertir la fuente a texto ni generar señales.

El análisis devuelve estadísticas vacías y entropía 0.0 para entrada vacía.
Huffman rechaza probabilidades vacías con `ValueError`. Para símbolo único,
asigna "0", longitud promedio 1 y varianza 0. La eficiencia rechaza entropía
negativa y longitud promedio no positiva. El principal rechaza el archivo vacío antes de llamar a Huffman.

## Integración futura

El orquestador conecta análisis → Huffman → codificación utilizando las
estructuras de [`common`](../common/README.md). La lectura corresponde a las
utilidades de archivos y la preparación del informe a `common/report_utils.py`.
La codificación de canal y la modulación son etapas posteriores sin módulos
en esta versión.

Al implementar, reemplazar las pruebas del placeholder correspondiente por
pruebas funcionales y actualizar este documento y el [README general](../README.md).

## Estado del codificador

Devuelve bits concatenados en orden, una cadena vacía para entrada vacía y
`ValueError` para símbolos sin código. No modifica el diccionario. La lista de
palabras se limita a un bloque; la cadena final y los fragmentos completos
permanecen en memoria durante la concatenación. No se empaquetan bits ni se
han realizado mediciones de tiempo o memoria.

Las pruebas funcionales e integraciones están en `tests/test_transmitter.py`.
Las integraciones se omiten mientras sus dependencias lancen
`NotImplementedError`. La decodificación está implementada y las pruebas de ida y vuelta pasan.

## Política de errores y archivo vacío

`calculate_entropy` omite términos de probabilidad cero y rechaza probabilidades
negativas con `ValueError`. El análisis de bytes sigue admitiendo la fuente
vacía como resultado estadístico, sin cambiar su contrato.

El principal lee el archivo y, si no contiene bytes, muestra un mensaje de
rechazo y termina antes de Huffman. No produce un archivo recibido ni modifica
uno existente. No calcula eficiencia ni simula una transmisión exitosa.
Huffman conserva su `ValueError` para el diccionario vacío; su algoritmo no
fue modificado. Se actualizaron únicamente sus docstrings.

Los archivos no vacíos ejecutan análisis, Huffman, eficiencia y codificación.
La lectura que falla por ausencia del archivo conserva el recorrido conceptual;
otros errores de E/S se muestran como errores y detienen el proceso.
