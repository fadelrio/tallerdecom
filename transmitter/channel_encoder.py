"""Contratos de codificación de canal por palabra y por flujo."""

from common.data_types import ChannelCodeConfig, EncodedChannel, EncodedSource


def encode_channel_word(message_bits: str, code: ChannelCodeConfig) -> str:
    """Codifica un mensaje binario con la matriz generadora del código.

    Args:
        message_bits: Cadena de exactamente k caracteres '0' o '1'.
        code: Parámetros n y k y matriz generadora binaria G de forma (k, n).

    Returns:
        Palabra binaria de n bits. Los últimos k bits contienen el mensaje.

    Raises:
        ValueError: Si el mensaje tiene longitud incorrecta o bits inválidos.
        NotImplementedError: Mientras la codificación por palabra esté pendiente.

    Notes:
        La palabra se obtiene como el producto del mensaje fila por G en GF(2).
    """
    raise NotImplementedError("Codificación de canal por palabra pendiente.")


def encode_channel(source: EncodedSource, code: ChannelCodeConfig) -> EncodedChannel:
    """Codifica la secuencia de bits Huffman en bloques de canal.

    Args:
        source: Bits Huffman como cadena de caracteres '0' y '1'.
        code: Parámetros compartidos del código lineal de bloques.

    Returns:
        Palabras de canal concatenadas y cantidad original de bits Huffman.
        Para una fuente vacía, devuelve un flujo vacío y longitud cero.

    Raises:
        ValueError: Si la fuente contiene bits inválidos.
        NotImplementedError: Mientras la codificación por flujo esté pendiente.

    Notes:
        Agrupa los bits en orden de llegada. Completa con ceros a la derecha
        el último grupo si tiene menos de k bits y usa encode_channel_word
        para codificar cada grupo.
    """
    raise NotImplementedError("Codificación de canal por flujo pendiente.")
