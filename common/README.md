# Datos y utilidades comunes

- `__init__.py`: paquete compartido.
- `data_types.py`: estadísticas, código, fuente codificada, comparación y
  estructuras de informe. Los símbolos son `str` de un carácter, los tamaños
  son cantidades de caracteres. `minimum_length` es H(X), de tipo `float`.
  `EncodedSource.iter_codewords` expone las palabras binarias en orden.
  Agrega `ModulatedData`, `Constellation`, `DemodulatedData`,
  `EnergyStatistics`, `ErrorRates` y `SymbolStatistics`, sin cálculos nuevos.
- `file_utils.py`: lee y escribe UTF-8 con `newline=''` y compara textos sin
  normalización. No conoce Huffman. Implementado.
- `report_utils.py`: `build_source_table` prepara filas por carácter;
  `build_coding_report` calcula métricas y totales con referencia Windows-1252.
  `format_source_report` devuelve Markdown con las seis secciones de datos del apartado B.
  `print_source` y `print_huffman` siguen disponibles para pruebas manuales.
  Para caracteres fuera de Windows-1252 se indica que la referencia no es aplicable.
- `README.md`: contratos y estado del paquete.

## Modulación: estado de los archivos

- `constellations.py` contiene `build_constellation(config)`. Devuelve coordenadas
  `(M, 1)` para PAM o `(M, M)` para FSK ortogonal coherente. El etiquetado
  Gray o binario sigue el orden de los niveles PAM o de los ejes FSK. La tabla
  se comparte entre transmisión, recepción y gráficos.
- `modulation_metrics.py` contiene `theoretical_error_rates` para SER y BER en
  AWGN. En PAM pondera las transiciones entre regiones por la distancia de
  Hamming. En FSK ortogonal calcula la SER mediante cuadratura y usa la
  simetría para obtener la BER. `symbol_statistics` cuenta las apariciones
  de cada símbolo y conserva las etiquetas sin observaciones.
- `modulation_plots.py` contiene `plot_constellation`. Guarda un PNG con
  etiquetas, regiones y una superposición opcional de muestras recibidas.
  FSK de más de dos dimensiones se muestra en un corte ortonormal.
  `plot_symbol_histogram` grafica conteos y frecuencias e indica la referencia 1/M.
- `modulation_report.py`: `format_modulation_report` implementado. Recibe
  configuración, energías y errores teóricos/estimados y estadísticas;
  devuelve Markdown con tablas y unidades, sin calcular métricas ni escribir
  archivos. Valida la configuración, conserva símbolos con conteo cero,
  escapa etiquetas para las tablas y exige longitudes alineadas del histograma.
  El llamador indica el Eb/N0 de la referencia AWGN y las condiciones de
  simulación. La interpretación académica corresponde a los estudiantes.

## Convenciones de los contratos

`Constellation.symbols` y `.labels` se corresponden fila a fila.
`ModulatedData.flag_descarte` indica si se descartó un grupo incompleto.
`DemodulatedData.symbols` contiene las coordenadas decididas de los símbolos
transmitidos y `.bits` contiene sus etiquetas concatenadas. `SymbolStatistics`
conserva `labels`, `counts` y `probabilities` en el orden de la constelación.

`EnergyStatistics` distingue `symbol_energy` (Es), `channel_bit_energy` (Ec)
y `bit_energy` (Eb de información). La relación de referencia es
`Ec = Es / log2(M)` y `Eb = Ec / code_rate`. La estimación actual devuelve
`Eb = Ec` para todas las tasas. Esto coincide con la referencia cuando la
tasa es 1 y queda pendiente el ajuste de `Eb` para tasas menores.

`ErrorRates` contiene las tasas numéricas `symbol_error_rate` y `bit_error_rate`.
`estimate_bit_error_rate` devuelve `BitErrorRate` con `error_rate`, `bits_vistos`
y `bits_errados`. Cuenta como error cada bit sin contraparte y usa la longitud
de la secuencia más larga como denominador. Ambas cadenas deben ser no vacías.

Las referencias teóricas suponen símbolos equiprobables, AWGN y recepción
coherente. `Eb/N0` se da en dB respecto del bit de información. Las tasas se
refieren a las decisiones del demodulador, antes de cualquier decodificación
de canal. La SER medida compara los símbolos transmitidos con los decididos.

Las [pruebas de métricas](../tests/test_modulation_metrics.py) documentan
resultados esperados para ejemplos pequeños.
