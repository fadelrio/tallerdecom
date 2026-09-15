# Pruebas automatizadas

Las pruebas usan `pytest` y verifican la arquitectura, la codificación de
fuente implementada y las integraciones cuyas dependencias estén disponibles.
La lectura binaria está implementada; escritura y comparación siguen pendientes.

## Archivos y trabajo pendiente

| Archivo | Responsabilidad actual | Qué implementar posteriormente |
| --- | --- | --- |
| `__init__.py` | Identifica y documenta el paquete de pruebas. | No requiere lógica adicional. |
| `test_source.py` | Comprueba imports, dataclasses, interfaces, placeholders, configuración y ejecución del principal. | Agregar pruebas de comportamiento por cada funcionalidad implementada y reemplazar su expectativa de `NotImplementedError`. |
| `test_main.py` | Verifica lectura binaria, rechazo del vacío y ejecución del transmisor. | Integrar pruebas del receptor cuando esté implementado. |
| `test_transmitter.py` | Prueba codificación por bloques e integración de fuente. | Las integraciones se activan al implementar los módulos pendientes. |
| `README.md` | Explica qué se prueba y cómo ampliar y ejecutar la suite. | Mantenerlo actualizado con la cobertura real. |

## Cobertura actual

- `test_modules_import`: importación de cada módulo listado en `MODULES`.
- `test_data_structures`: instanciación y documentación de las dataclasses con
  datos manuales; incluye símbolos 0 y 255.
- `test_function_contracts`: firmas, anotaciones y docstrings de las funciones
  listadas en `CONTRACTS`.
- `test_placeholders_are_explicit`: espera `NotImplementedError` en las interfaces seleccionadas. La selección excluye las funciones implementadas, incluida eficiencia y lectura.
- `test_config_paths`: rutas `Path` distintas para entrada y salida.
- `test_main_runs_without_input_file`: ejecución del principal en un proceso
  independiente, mensajes de estado y ausencia de archivos en su directorio
  temporal de trabajo.

Consultar `python -m pytest -q -rs` para ver casos aprobados y omitidos.

## Cómo ejecutar

Crear el entorno e instalar dependencias según [ENTORNO.md](../ENTORNO.md).
Con el entorno activado, ejecutar desde la raíz que contiene `main.py`:

```bash
python -m pytest
python -m pytest tests/test_source.py -q
```

Los comandos son alternativas para ejecutar toda la suite o solo este archivo.

## Ampliaciones al implementar funcionalidades

1. Mantener las pruebas de imports y contratos, ajustándolas si se acuerda
   un cambio de interfaz.
2. Excluir la función implementada de los casos de placeholders. La selección excluye codificación, análisis, decodificación y construcción
   de Huffman, que ya cuentan con pruebas funcionales o de integración.
   Para las otras interfaces pendientes, actualizar la selección por nombre.
3. Añadir resultados conocidos para conteos, probabilidades, entropía,
   longitudes, varianza, eficiencia y propiedad de prefijo.
4. Probar codificación y decodificación con bytes no imprimibles, y comprobar
   la recuperación exacta mediante una prueba de ida y vuelta.
5. Probar E/S binaria y comparación con archivos en `tmp_path`, y las filas
   y métricas del informe con resultados esperados independientes.
6. Definir y cubrir casos límite, como fuente vacía y símbolo único, junto
   con las políticas de cada implementación.
7. Adaptar las pruebas del orquestador cuando conecte operaciones reales y
   actualizar el estado del [README general](../README.md).

Estas ampliaciones están pendientes; no deben exigir algoritmos funcionales
mientras sus interfaces sigan siendo placeholders.

## Pruebas de codificación e integración

`test_transmitter.py` comprueba ejemplos conocidos, entrada vacía, todos los
valores byte, ausencia de mutación del diccionario, límites de bloque y errores
por símbolos sin código, incluso en bloques posteriores.

Las pruebas de análisis y de ida y vuelta usan códigos manuales para poder
probar las contribuciones de análisis y decodificación sin esperar a Huffman.
Otras pruebas integran el transmisor completo y el recorrido completo de
fuente; requieren también `build_huffman_code` implementado.

El auxiliar `_available` omite únicamente una llamada que lance
`NotImplementedError`. Al implementar una interfaz se activan automáticamente
sus comprobaciones; una aserción incorrecta u otra excepción falla. Retirar
este mecanismo temporal cuando los módulos estén completos para que ningún
`NotImplementedError` quede oculto como omisión en la suite final.
No se agregaron benchmarks de tiempo o memoria.

## Resultado y cobertura de errores

La suite da **59 aprobadas y 3 omitidas**. Las omisiones corresponden al
receptor pendiente. Eficiencia y lectura ya no se prueban como placeholders.

Las pruebas nuevas comprueban eficiencia conocida y cero, rechazo de entropía
negativa y longitud no positiva, entropía con probabilidades cero o negativas,
y los contratos de análisis y Huffman para entrada vacía.

`test_main.py` verifica lectura binaria exacta, que un archivo vacío no llegue
a Huffman ni modifique una salida existente, y que una entrada válida ejecute
el transmisor sin invocar la decodificación pendiente. No hay benchmarks.
