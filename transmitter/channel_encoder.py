"""Contratos de codificación de canal por palabra y por flujo."""

import numpy as np

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

    Notes:
        La palabra se obtiene como el producto del mensaje fila por G en GF(2),
        es decir, multiplicando como enteros y tomando módulo 2. Como G tiene
        la forma [P | I_k], el producto resulta [m·P | m]: los bits de paridad
        a la izquierda y el mensaje sin modificar a la derecha.
    """
    if len(message_bits) != code.k:
        raise ValueError(f"El mensaje debe tener exactamente {code.k} bits.")

    if not set(message_bits) <= {"0", "1"}:
        raise ValueError("El mensaje solo puede contener los caracteres '0' y '1'.")

    message = np.array([int(bit) for bit in message_bits], dtype=np.int64)
    generator = np.asarray(code.generator_matrix, dtype=np.int64)

    # Producto mensaje fila por G en GF(2): suma módulo 2.
    codeword = (message @ generator) % 2

    return "".join(str(bit) for bit in codeword)


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

    Notes:
        Agrupa los bits en orden de llegada. Completa con ceros a la derecha
        el último grupo si tiene menos de k bits y usa encode_channel_word
        para codificar cada grupo. Como hay a lo sumo 2**k mensajes distintos,
        cada uno se codifica una sola vez y se reutiliza el resultado.
    """
    bits = source.bits

    if not set(bits) <= {"0", "1"}:
        raise ValueError("La fuente solo puede contener los caracteres '0' y '1'.")

    if not bits:
        return EncodedChannel(bits="", source_bit_length=0)

    # Relleno con ceros a la derecha hasta completar el último grupo.
    missing_bits = -len(bits) % code.k
    padded_bits = bits + "0" * missing_bits

    codewords = []
    known_words: dict[str, str] = {}

    for start in range(0, len(padded_bits), code.k):
        message = padded_bits[start:start + code.k]

        if message not in known_words:
            known_words[message] = encode_channel_word(message, code)

        codewords.append(known_words[message])

    return EncodedChannel(
        bits="".join(codewords),
        source_bit_length=len(bits),
    )