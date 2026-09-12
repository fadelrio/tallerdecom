"""Contrato de codificación de fuente."""

from common.data_types import EncodedSource


def encode_source(data: bytes, codebook: dict[int, str]) -> EncodedSource:
    """Codificará una fuente binaria mediante su código Huffman.

    Args:
        data: Secuencia original de bytes.
        codebook: Palabra binaria correspondiente a cada símbolo entero 0..255.

    Returns:
        Secuencia codificada como cadena de caracteres '0' y '1'.

    Raises:
        NotImplementedError: La funcionalidad está pendiente.

    Notes:
        Deberá reemplazar cada símbolo por su palabra Huffman y concatenar
        las palabras en el orden original, sin interpretar el archivo
        como texto.
    """
    raise NotImplementedError("Codificación de fuente pendiente.")
