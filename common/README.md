# Utilidades y datos compartidos

Este paquete define los datos que intercambian los módulos y las interfaces
de archivos e informe de los apartados A/B. La fuente se conserva como `bytes`
y cada símbolo como un entero entre 0 y 255.

## Archivos y trabajo pendiente

| Archivo | Responsabilidad actual | Qué implementar posteriormente |
| --- | --- | --- |
| `__init__.py` | Identifica y documenta el paquete. | No requiere lógica adicional; mantenerlo sin efectos secundarios al importar. |
| `data_types.py` | Define las siete dataclasses compartidas y documenta sus atributos. | Las estructuras ya están definidas. Mantener sus contratos al conectar las funcionalidades; los cálculos corresponden a los otros módulos. |
| `file_utils.py` | Declara `read_file`, `write_file` y `compare_data`. | Leer y escribir en modo binario mediante rutas `Path`; comparar igualdad exacta y tamaños y devolver `FileComparison`. |
| `report_utils.py` | Declara `build_source_table` y `build_coding_report`. | Preparar filas por símbolo y métricas comparativas a partir de los resultados de fuente y Huffman. |
| `README.md` | Describe responsabilidades y pendientes del paquete. | Actualizarlo cuando cambien las interfaces o su implementación. |

## Estructuras de datos

- `SourceStatistics`: conteos, probabilidades, total de símbolos y entropía.
- `CodeStatistics`: longitud mínima, promedio, varianza y propiedad de prefijo.
- `HuffmanResult`: diccionario de palabras Huffman y estadísticas del código.
- `EncodedSource`: secuencia de bits como cadena de `'0'` y `'1'`.
- `FileComparison`: igualdad y tamaños original y recibido en bytes.
- `SourceReport`: símbolo, cantidad, probabilidad y palabra Huffman.
- `CodingReport`: entropía, longitud mínima y promedio, varianza, eficiencia,
  longitud fija de referencia y totales de bits Huffman y fijo.

## Implementación futura del informe

`build_source_table` deberá producir una fila por símbolo observado, conservando
el símbolo como entero incluso para bytes de control.

`build_coding_report` deberá reunir las estadísticas, utilizar
`calculate_efficiency` para obtener la fracción `H(X) / L_promedio`, tomar la
longitud de `encoded.bits` como total Huffman y comparar con un código fijo
de 8 bits por símbolo. La conversión a porcentaje y la representación legible
de símbolos pertenecen a la presentación. No se generan documentos PDF o Word.

## Estado y límites

Las dataclasses están disponibles y no realizan cálculos ni validaciones.
Todas las funciones de `file_utils.py` y `report_utils.py` son placeholders que
lanzan `NotImplementedError`. Las utilidades de archivos no deben depender de
Huffman y `data_types.py` no debe depender del transmisor ni del receptor.

Al implementar una interfaz, actualizar sus docstrings, las pruebas en
[`tests/`](../tests/README.md) y el [estado general](../README.md).
