# Pruebas automáticas

- `__init__.py`: paquete de pruebas.
- `test_source.py`: imports, dataclasses, interfaces textuales; ejecución del principal sin entrada.
- `test_transmitter.py`: codificación por bloques, análisis, Huffman, entropía,
  eficiencia e ida y vuelta; Unicode, acentos y palabras por carácter.
- `test_main.py`: E/S UTF-8, preservación de BOM y CR/LF/CRLF, rechazo del vacío,
  UTF-8 inválido e integración del sistema con archivos temporales.
- `test_report.py`: tablas, métricas, totales, muestra y referencia no aplicable.
- `README.md`: documentación de pruebas.

Desde la raíz con el entorno activo: `python -m pytest -q -rs`.
Los datos fuente son texto; los bytes se usan únicamente para comprobar el
contenido físico de archivos UTF-8 o generar una entrada inválida.

Pendiente: más casos de diccionarios malformados y mayor cobertura de formatos de presentación. Los scripts manuales están en `experiments/`; no se recolectan.

La selección por terminal se prueba con archivos temporales de nombre propio
 y de estilo Gutenberg, preservando encabezados y CRLF. No se descarga ninguna
obra durante las pruebas ni se necesita conexión a Internet.
