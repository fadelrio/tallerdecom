"""Contrato de decodificación de fuente."""

from common.data_types import EncodedSource


def decode_source(encoded: EncodedSource, codebook: dict[int, str]) -> bytes:
    """Reconstruirá la secuencia original de símbolos.

    Args:
        encoded: Secuencia binaria representada como cadena de bits.
        codebook: Palabras Huffman asociadas a símbolos enteros 0..255.

    Returns:
        Bytes reconstruidos a partir de la secuencia binaria y el código.

    Raises:
        NotImplementedError: La funcionalidad está pendiente.

    Notes:
        Deberá reconocer las palabras del código y recuperar los símbolos
        originales sin efectuar conversiones de codificación de texto.
    """
    raise NotImplementedError("Decodificación de fuente pendiente.")
