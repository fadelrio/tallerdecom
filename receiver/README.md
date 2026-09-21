# Receptor: decodificación de fuente

La decodificación está implementada mediante un árbol binario. Recupera los
bytes originales y pasa las pruebas de ida y vuelta con el transmisor.

## Archivos

- `__init__.py`: identifica el paquete; no requiere lógica adicional.
- `source_decoder.py`: `decode_source(encoded, codebook) -> bytes` construye
  el árbol a partir del diccionario y recorre la secuencia de bits. Pendiente:
  completar validaciones del diccionario y conectar el receptor en `main.py`.
- `README.md`: estado, contratos y trabajo pendiente del receptor.

## Comportamiento actual

Los símbolos son enteros 0..255. Se devuelve `bytes`, sin interpretación de
texto. Con un código válido, una secuencia vacía devuelve `b""`. Se rechazan
bits de entrada distintos de 0/1, palabras duplicadas, recorridos incompatibles
con el árbol y secuencias que terminan con una palabra incompleta.

La función requiere un diccionario prefijo con palabras binarias no vacías.
Actualmente no valida completamente esa precondición: una letra en una palabra
se trata como una rama derecha; tampoco se detectan todos los conflictos de
prefijos o palabras vacías. No se debe usar con diccionarios arbitrarios sin
validar. Estas limitaciones no se corrigieron en esta revisión.

## Validación recomendada (pendiente)

Al construir el árbol, comprobar símbolos enteros 0..255 y palabras no vacías
formadas solo por 0/1. Si se intenta continuar desde una hoja, una palabra
anterior es prefijo de la nueva. Si el nodo final ya tiene hijos, la nueva
palabra es prefijo de otra. Rechazar ambos casos y palabras duplicadas con
`ValueError`. Así se comprueba el código mientras se construye el árbol, sin
comparar todas las parejas de palabras. Agregar pruebas para ambos órdenes de
inserción del conflicto, caracteres inválidos y palabras vacías.

## Integración

`main.py` todavía no llama al receptor. Escritura y comparación siguen pendientes
en `common/file_utils.py`. Las pruebas de `tests/test_transmitter.py` ya ejecutan
la recuperación completa. La demodulación y decodificación de canal son futuras.
