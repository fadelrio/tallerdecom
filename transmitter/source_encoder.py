"""Codificación de fuente por bloques con salida como cadena binaria."""

from common.data_types import EncodedSource


# Cantidad de bytes de entrada por bloque, no de bits de salida. Este tamaño
# acota la lista temporal; no es un parámetro del algoritmo de Huffman.
_BLOCK_SIZE = 64 * 1024


def encode_source(data: bytes, codebook: dict[int, str]) -> EncodedSource:
    """Codifica los bytes en orden mediante palabras Huffman por bloques.

    Args:
        data: Secuencia original de bytes, incluidos valores no imprimibles.
        codebook: Palabra binaria válida de cada símbolo entero 0..255.

    Returns:
        Secuencia de caracteres '0' y '1'; vacía si data está vacío.

    Raises:
        ValueError: Si algún símbolo de entrada no tiene código asignado.

    Notes:
        Procesa bloques de hasta 64 KiB para acotar la lista temporal de
        palabras. No interpreta texto ni modifica las entradas. Se asume
        un código prefijo válido, con palabras no vacías, construido por
        Huffman. Su validación corresponde a ese módulo.
        La entrada y los fragmentos codificados permanecen en memoria; la
        concatenación final puede coexistir con los fragmentos. Esta interfaz
        no realiza streaming ni empaqueta bits en bytes.
    """
    # Conservamos un texto por bloque para evitar una lista de palabras
    # con una referencia por cada byte del archivo completo.
    fragments: list[str] = []
    for start in range(0, len(data), _BLOCK_SIZE):
        # El último bloque puede ser más corto: el slicing lo admite sin
        # relleno. Los límites de bloque no agregan separadores a la salida.
        block = data[start:start + _BLOCK_SIZE]
        try:
            # Iterar bytes entrega enteros 0..255, las claves del código.
            # join une las palabras en orden sin concatenaciones sucesivas
            # de una cadena creciente. La lista temporal termina aquí.
            fragments.append("".join([codebook[symbol] for symbol in block]))
        except KeyError as error:
            # Una clave ausente significa que no podemos codificar la fuente
            # completa. No devolvemos un resultado parcial ni omitimos bytes.
            # Conservamos la excepción original como causa para depuración.
            symbol = error.args[0]
            raise ValueError(
                f"El símbolo {symbol} no tiene código Huffman asignado."
            ) from error
    # La interfaz exige una única cadena: esta unión conserva en memoria los
    # fragmentos mientras construye el resultado. Para entrada vacía, el
    # bucle no se ejecuta y join devuelve naturalmente una cadena vacía.
    return EncodedSource(bits="".join(fragments))
