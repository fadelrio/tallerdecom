# Pruebas automatizadas

Las pruebas usan `pytest` y actualmente verifican el esqueleto del proyecto.
No afirman que los algoritmos ni las operaciones de archivos estén implementados.

## Archivos y trabajo pendiente

| Archivo | Responsabilidad actual | Qué implementar posteriormente |
| --- | --- | --- |
| `__init__.py` | Identifica y documenta el paquete de pruebas. | No requiere lógica adicional. |
| `test_source.py` | Comprueba imports, dataclasses, interfaces, placeholders, configuración y ejecución del principal. | Agregar pruebas de comportamiento por cada funcionalidad implementada y reemplazar su expectativa de `NotImplementedError`. |
| `README.md` | Explica qué se prueba y cómo ampliar y ejecutar la suite. | Mantenerlo actualizado con la cobertura real. |

## Cobertura actual

- `test_modules_import`: importación de cada módulo listado en `MODULES`.
- `test_data_structures`: instanciación y documentación de las dataclasses con
  datos manuales; incluye símbolos 0 y 255.
- `test_function_contracts`: firmas, anotaciones y docstrings de las funciones
  listadas en `CONTRACTS`.
- `test_placeholders_are_explicit`: las diez interfaces pendientes lanzan
  `NotImplementedError`; no se esperan resultados calculados.
- `test_config_paths`: rutas `Path` distintas para entrada y salida.
- `test_main_runs_without_input_file`: ejecución del principal en un proceso
  independiente, mensajes de estado y ausencia de archivos en su directorio
  temporal de trabajo.

La parametrización produce actualmente 37 casos de prueba.

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
2. Excluir la función implementada de los casos de placeholders. Actualmente
   se seleccionan mediante `CONTRACTS[:-2]`; habrá que actualizar esa selección
   para que solo incluya las funciones que sigan pendientes.
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
