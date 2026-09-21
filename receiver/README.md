# Receptor

- `__init__.py`: identifica el paquete.
- `source_decoder.py`: reconstruye `str` desde `EncodedSource` y un diccionario
  `dict[str, str]`. Construye un árbol y acumula caracteres, no bytes.
- `README.md`: documentación y limitaciones.

La decodificación está implementada y conectada al principal. Preserva acentos,
controles y puntos de código sin normalizarlos. Rechaza bits de entrada
inválidos, palabras duplicadas, recorridos incompatibles y palabras incompletas.

Requiere un código prefijo válido con palabras binarias no vacías. Sigue
pendiente validar por completo el diccionario: caracteres de código inválidos,
palabras vacías y conflictos de prefijos en ambos órdenes de inserción.
La migración textual no modifica esa lógica. Escritura y comparación se hacen
en `common/file_utils.py`; demodulación y decodificación de canal son futuras.
