# Pruebas manuales

Espacio para scripts exploratorios escritos y ejecutados por los colaboradores.
No es necesario convertirlos en herramientas con argumentos ni tests pytest.

## Archivos

- `test_B.py`: original trasladado desde `tests/test_B.py`, con los ajustes de interfaz necesarios para texto. Lee `textito.txt`, imprime análisis y Huffman, muestra el código
  del salto de línea y la fuente codificada completa.
- `experimento_PAM.py`: `run_pam_experiment(config)` lee el archivo configurado,
  reutiliza Huffman y PAM existentes con M=16, y muestra relleno, dimensiones
  y las primeras coordenadas. No escribe el archivo recibido ni genera gráficos.
  El bloque `if __name__ == "__main__":` llama a la función local; importar el
  módulo no ejecuta simulaciones. No depende de `main.run_simulation`.
- `__init__.py`: permite ejecutar los scripts como módulos desde la raíz.
- `README.md`: instrucciones para las pruebas manuales.

## Ejecución

Con el entorno virtual activado, desde la raíz del proyecto:

```bash
python -m experiments.test_B
python -m experiments.experimento_PAM
```

`textito.txt` debe estar en el directorio de trabajo (la raíz con este comando).
El script original requiere al menos un salto de línea, porque consulta
 directamente el carácter \n del diccionario Huffman. El resultado decodificado ahora es str y se imprime directamente. Se mantienen estas
condiciones y la impresión completa de bits tal como estaban.

En un IDE, seleccionar el módulo `experiments.test_B`, el intérprete del entorno
virtual y la raíz del proyecto como directorio de trabajo.

El experimento PAM usa las rutas de `load_config()` y la configuración de
modulación indicada dentro de su función. Se puede editar esa selección para
explorar PAM. FSK, demodulación, mediciones y gráficos siguen pendientes; no
se invocan sus esqueletos desde este script. NumPy debe estar instalado según
`requirements.txt`.

## Nuevas pruebas

Agregar los scripts a esta carpeta y documentar sus entradas y comandos aquí.
Pueden conservar el estilo de script manual que necesite cada colaborador.

`pytest.ini` limita la búsqueda automática a `tests/`: `python -m pytest` no
importa estas pruebas manuales. No pasar `experiments/` explícitamente a pytest,
ya que hacerlo anula esa selección inicial.
