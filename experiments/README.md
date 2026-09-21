# Pruebas manuales

Espacio para scripts exploratorios escritos y ejecutados por los colaboradores.
No es necesario convertirlos en herramientas con argumentos ni tests pytest.

## Archivos

- `test_B.py`: original trasladado desde `tests/test_B.py`, con los ajustes de interfaz necesarios para texto. Lee `textito.txt`, imprime análisis y Huffman, muestra el código
  del salto de línea y la fuente codificada completa.
- `__init__.py`: permite ejecutar los scripts como módulos desde la raíz.
- `README.md`: instrucciones para las pruebas manuales.

## Ejecución

Con el entorno virtual activado, desde la raíz del proyecto:

```bash
python -m experiments.test_B
```

`textito.txt` debe estar en el directorio de trabajo (la raíz con este comando).
El script original requiere al menos un salto de línea, porque consulta
 directamente el carácter \n del diccionario Huffman. El resultado decodificado ahora es str y se imprime directamente. Se mantienen estas
condiciones y la impresión completa de bits tal como estaban.

En un IDE, seleccionar el módulo `experiments.test_B`, el intérprete del entorno
virtual y la raíz del proyecto como directorio de trabajo.

## Nuevas pruebas

Agregar los scripts a esta carpeta y documentar sus entradas y comandos aquí.
Pueden conservar el estilo de script manual que necesite cada colaborador.

`pytest.ini` limita la búsqueda automática a `tests/`: `python -m pytest` no
importa estas pruebas manuales. No pasar `experiments/` explícitamente a pytest,
ya que hacerlo anula esa selección inicial.
