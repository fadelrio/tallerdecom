# Pruebas automáticas

- `__init__.py`: paquete de pruebas.
- `test_source.py`: imports, dataclasses, interfaces textuales; ejecución del principal sin entrada.
- `test_transmitter.py`: codificación por bloques, análisis, Huffman, entropía,
  eficiencia e ida y vuelta; Unicode, acentos y palabras por carácter.
- `test_main.py`: E/S UTF-8, preservación de BOM y CR/LF/CRLF, rechazo del vacío,
  UTF-8 inválido e integración del sistema con archivos temporales.
- `test_report.py`: tablas, métricas, totales, muestra y referencia no aplicable.
- `test_modulation_contracts.py`: imports, firmas, anotaciones, estructuras,
  campos opcionales de configuración y pruebas de la antigua entrada PAM.
- `test_modulation.py` cubre PAM, FSK, constelaciones Gray/binarias y
  normalización de energía.
- `test_modulation_config.py`: validación activa de tipos, valores finitos,
  tasas de código y conexión del cargador con el validador completo.
- `test_demodulation.py`: decisiones conocidas, empates, etiquetas, dimensiones,
  tasa de canal e ida y vuelta PAM/FSK para M=2, 4, 8 y 16. Algunos casos
  conservan la expectativa anterior de relleno.
- `test_modulation_metrics.py`: ejemplos manuales de Es/Ec/Eb, SER, BER,
  referencias binarias coherentes en AWGN e histogramas con conteos cero.
- `test_modulation_presentation.py` verifica tablas Markdown y la creación
  de PNG de constelación e histograma.
- `test_modulation_main.py` verifica la orquestación, el informe de un bloque
  truncado, errores de E/S y la recuperación real de texto UTF-8 sin ruido.
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

## Pruebas del informe de modulación

```bash
python -m pytest -q tests/test_modulation_metrics.py tests/test_modulation_presentation.py tests/test_modulation_main.py
```

Las pruebas de gráficos requieren Matplotlib. Comprueban que se genere un
PNG de dimensiones positivas. Las etiquetas, regiones de decisión y
proyecciones se revisan visualmente en los gráficos generados.

## Fallos conocidos

En `1c596ee`, la suite completa registró 270 pruebas aprobadas y 57 fallidas.
Entre los casos pendientes se incluyen los siguientes.

- Algunos contratos de modulación todavía esperan las firmas antiguas, el
  relleno de bits o el módulo renombrado `experimento_PAM`.
- La estimación de `Eb` para una tasa de `0.5` devuelve `Ec`. La prueba espera
  `Eb = Ec / code_rate`.
- Siete casos de fuente e informe B fallan porque la muestra accede a las
  líneas 127 y 128 en archivos más cortos. El error es `IndexError`.
