# Pruebas automáticas

- `__init__.py`: paquete de pruebas.
- `test_source.py`: imports, dataclasses, interfaces textuales; ejecución del principal sin entrada.
- `test_transmitter.py`: codificación por bloques, análisis, Huffman, entropía,
  eficiencia e ida y vuelta; Unicode, acentos y palabras por carácter.
- `test_main.py`: E/S UTF-8, preservación de BOM y CR/LF/CRLF, rechazo del vacío,
  UTF-8 inválido e integración del sistema con archivos temporales.
- `test_report.py`: tablas, métricas, totales, muestra y referencia no aplicable.
- `test_modulation_contracts.py`: imports, firmas, anotaciones, estructuras,
  campos opcionales de configuración e importación/entrada del experimento PAM.
- `test_modulation.py`: PAM y validación activos; futuros casos de
  constelaciones Gray/binarias, normalización de canal y FSK.
- `test_modulation_config.py`: validación activa de tipos, valores finitos,
  tasas de código y conexión del cargador con el validador completo.
- `test_demodulation.py`: decisiones conocidas, empates, etiquetas, dimensiones,
  relleno, tasa de canal e ida y vuelta PAM/FSK para M=2, 4, 8 y 16.
- `test_modulation_metrics.py`: ejemplos manuales de Es/Ec/Eb, SER, BER,
  referencias binarias coherentes en AWGN e histogramas con conteos cero.
- `test_modulation_presentation.py`: Markdown activo, preservación de valores,
  conteos cero, escape y alineación de filas; futura creación de PNG temporales.
- `test_modulation_main.py`: orquestación activa con bloques sustituidos,
  retiro de relleno una sola vez, referencia Eb/N0, propagación de pendientes
  y errores de E/S; futura recuperación real del archivo UTF-8 sin ruido.
- `_pending.py`: auxiliar de pruebas que omite solo llamadas que todavía
  lanzan `NotImplementedError`; las aserciones se ejecutan fuera del auxiliar.
- `README.md`: documentación de pruebas.

Desde la raíz con el entorno activo: `python -m pytest -q -rs`.
Los datos fuente son texto; los bytes se usan únicamente para comprobar el
contenido físico de archivos UTF-8 o generar una entrada inválida.

Pendiente: más casos de diccionarios malformados y mayor cobertura de formatos de presentación. Los scripts manuales están en `experiments/`; no se recolectan.

La selección por terminal se prueba con archivos temporales de nombre propio
 y de estilo Gutenberg, preservando encabezados y CRLF. No se descarga ninguna
obra durante las pruebas ni se necesita conexión a Internet.

## Estado de las pruebas de modulación

Los contratos, la configuración, el informe, la orquestación con bloques
sustituidos, el experimento reorganizado y PAM existente se comprueban
normalmente. Los casos funcionales pendientes tienen entradas y resultados
esperados, pero se omiten cuando la llamada bajo prueba lanza
`NotImplementedError`. Al implementar una función, sus casos empezarán a
verificarse automáticamente. Otros errores, incluidos los de validación o
resultados incorrectos, no se convierten en omisiones.

Los bloques sustituidos de la prueba de orquestación usan resultados manuales;
verifican las conexiones y no reemplazan las pruebas de algoritmos ni la
aceptación de punta a punta, que sigue pendiente de esos bloques.

Ejecutar `python -m pytest -q -rs` para ver qué funciones continúan pendientes.
No eliminar la excepción de un esqueleto hasta implementar su comportamiento.
No hay marcas de omisión permanentes ni pruebas vacías.

Los valores esperados se escriben explícitamente o se comparan con propiedades
del contrato; los tests no reproducen los algoritmos. Las pruebas de gráficos
solo comprobarán creación de PNG con dimensiones positivas: etiquetas,
regiones y proyecciones requerirán inspección visual al implementarlas.
No se requiere Matplotlib para recolectar esta suite; sí NumPy, que ya usa el
proyecto. La descarga de dependencias es un paso de preparación del entorno.

## Fallos previos del informe de fuente

La suite original presenta siete fallos: tres casos de `test_main.py` y cuatro
de `test_report.py`. `common/report_utils.py` selecciona las líneas con índices
126 y 127 sin comprobar que existan, por lo que fuentes pequeñas producen
`IndexError`. Se reprodujeron los mismos fallos sobre la versión original
del repositorio. Se conserva esa lógica, sin omitir los casos ni modificar
sus expectativas, porque este cambio solo organiza el apartado de modulación.
