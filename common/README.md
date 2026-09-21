# Datos y utilidades comunes

- `__init__.py`: paquete compartido.
- `data_types.py`: estadísticas, código, fuente codificada, comparación y
  estructuras de informe. Los símbolos son `str` de un carácter, los tamaños
  son cantidades de caracteres. `minimum_length` es H(X), de tipo `float`.
  `EncodedSource.iter_codewords` expone las palabras binarias en orden.
- `file_utils.py`: lee y escribe UTF-8 con `newline=''` y compara textos sin
  normalización. No conoce Huffman. Implementado.
- `report_utils.py`: `build_source_table` prepara filas por carácter;
  `build_coding_report` calcula métricas y totales con referencia Windows-1252.
  `format_source_report` devuelve Markdown con las seis secciones de datos del apartado B.
  `print_source` y `print_huffman` siguen disponibles para pruebas manuales.
  Para caracteres fuera de Windows-1252 se indica que la referencia no es aplicable.
- `README.md`: contratos y estado del paquete.
