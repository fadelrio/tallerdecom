# Receptor: decodificación de fuente

Este paquete define la interfaz para recuperar los bytes originales en el
apartado B. La decodificación todavía no está implementada.

## Archivos y trabajo pendiente

| Archivo | Responsabilidad actual | Qué implementar posteriormente |
| --- | --- | --- |
| `__init__.py` | Identifica y documenta el paquete del receptor. | No requiere lógica adicional; mantenerlo sin efectos secundarios al importar. |
| `source_decoder.py` | Declara `decode_source(encoded, codebook) -> bytes`. | Reconocer las palabras Huffman en la secuencia binaria y reconstruir los símbolos originales en orden. |
| `README.md` | Describe responsabilidades y pendientes del paquete. | Actualizarlo cuando se implemente o cambie la interfaz. |

## Contrato de decodificación

`decode_source` recibirá un `EncodedSource` cuya cadena contiene bits `'0'` y
`'1'`, y el diccionario `dict[int, str]` que asocia símbolos `0..255` con
palabras Huffman. Deberá devolver `bytes`, preservando controles y valores no
imprimibles sin convertirlos a texto.

Actualmente la función lanza `NotImplementedError`. Al implementarla habrá
que definir y probar el comportamiento para secuencias vacías, bits inválidos,
palabras incompletas y códigos inválidos, de forma consistente con el
transmisor. Estas políticas aún no están definidas.

## Integración y pruebas futuras

La escritura del archivo recibido y la comparación pertenecen a
`common/file_utils.py`; la conexión entre etapas corresponde a `main.py`.
La demodulación y la decodificación de canal pertenecen a etapas futuras.

Las pruebas deberán verificar ejemplos de decodificación conocidos y la
recuperación exacta de bytes tras codificar y decodificar, una vez disponibles
ambas operaciones. Se reemplazará la prueba que espera `NotImplementedError`
para esta interfaz y se actualizará el [README general](../README.md).
