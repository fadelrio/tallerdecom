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

El informe ya está implementado. Los demás archivos conservan interfaces con
`NotImplementedError`. La entrada `main.run_modulation_simulation` ya los
conecta, pero no puede completar una ejecución real hasta implementarlos.

- `constellations.py`: implementar `build_constellation(config)`. Devolver
  coordenadas `(M, 1)` para PAM o `(M, M)` para FSK ortogonal coherente, con
  etiquetas Gray/binarias por fila. Ordenar niveles PAM de menor a mayor y
  FSK por eje de base. Aplicar energía y tasa de canal. Esta tabla deberá
  ser compartida por transmisión, recepción y gráficos.
- `modulation_metrics.py`: implementar `estimate_energies` y
  `theoretical_energies`, distinguiendo Es, Ec y Eb; `estimate_symbol_error_rate`
  sobre símbolos transmitidos/decididos, `estimate_bit_error_rate` sobre bits
  sin relleno y `theoretical_error_rates(config, eb_n0_db)` para referencias
  en AWGN. Implementar también `symbol_statistics`, incluyendo símbolos de
  conteo cero. No suponer equiprobabilidad en las muestras observadas.
- `modulation_plots.py`: implementar `plot_constellation` con etiquetas y
  regiones, y `plot_symbol_histogram` con cantidades y probabilidades ya
  calculadas. Guardar PNG en la ruta recibida, cuyo directorio padre existe,
  sin abrir ventanas. Para FSK de dimensión mayor que tres explicar qué
  proyección o representación se muestra. Matplotlib será una dependencia
  futura: no se importa ni se necesita para los contratos actuales.
- `modulation_report.py`: `format_modulation_report` implementado. Recibe
  configuración, energías y errores teóricos/estimados y estadísticas;
  devuelve Markdown con tablas y unidades, sin calcular métricas ni escribir
  archivos. Valida la configuración, conserva símbolos con conteo cero,
  escapa etiquetas para las tablas y exige longitudes alineadas del histograma.
  El llamador indica el Eb/N0 de la referencia AWGN y las condiciones de
  simulación. La interpretación académica corresponde a los estudiantes.

## Convenciones de los contratos

`Constellation.symbols` y `.labels` se corresponden fila a fila.
`DemodulatedData.symbols` conserva también el símbolo que contenía relleno;
`.bits` ya no lo incluye. `EnergyStatistics` usa `symbol_energy` (Es),
`channel_bit_energy` (Ec) y `bit_energy` (Eb de información). `ErrorRates`
contiene `symbol_error_rate` y `bit_error_rate`. `SymbolStatistics` conserva
`labels`, `counts` enteros y `probabilities`, en el orden de la constelación.

Las referencias teóricas suponen símbolos equiprobables, AWGN y recepción
coherente. Eb/N0 se da en dB respecto de información; con código de canal,
la referencia será previa a decodificarlo, sin atribuirle ganancia de código.
Documentar las aproximaciones de BER que se elijan al implementar.
Las métricas rechazarán secuencias vacías, dimensiones incompatibles o datos
inválidos; SER compara símbolos decididos, no las observaciones con ruido.

Los resultados esperados de ejemplos pequeños están escritos en los tests;
las pruebas no contienen implementaciones de los algoritmos pendientes.
