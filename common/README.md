# Datos y utilidades comunes

- `__init__.py`: paquete compartido.
- `data_types.py`: estadísticas, código, fuente codificada, comparación y
  estructuras de informe. Los símbolos son `str` de un carácter, los tamaños
  son cantidades de caracteres. `minimum_length` es H(X), de tipo `float`.
  `EncodedSource.iter_codewords` expone las palabras binarias en orden.
- `file_utils.py`: lee y escribe UTF-8 con `newline=''` y compara textos sin
  normalización. No conoce Huffman. Implementado.
- `report_utils.py`: `print_source` y `print_huffman` imprimen caracteres y
  controles con representación escapada. `build_source_table` y
  `build_coding_report` siguen pendientes: preparar filas y métricas científicas,
  manteniendo separada su presentación. Acordar una tabla de 8 bits antes de
  calcular la referencia fija; rechazar caracteres no representables.
- `README.md`: contratos y estado del paquete.
