"""Contratos de decodificación de canal mediante síndromes."""

import numpy as np

from common.data_types import ChannelWordDecoding, DecodedChannel, SyndromeTable


def decode_channel_word(
    received_word: str,
    parity_check_matrix: np.ndarray,
    syndrome_table: SyndromeTable,
) -> ChannelWordDecoding:
    """Calcula el síndrome de una palabra y corrige errores según la tabla.

    Args:
        received_word: Palabra de n caracteres '0' o '1'.
        parity_check_matrix: Matriz binaria H de forma (n-k, n).
        syndrome_table: Tabla completa de síndromes y líderes de coset de H.

    Returns:
        Palabra resultante, síndrome original y máscara aplicada. Para un
        síndrome cero, la máscara es de ceros. Si un error detectado se deja
        sin corregir, devuelve la palabra recibida y la máscara es None.

    Raises:
        ValueError: Si la palabra tiene longitud incorrecta o bits inválidos.
        NotImplementedError: Mientras la decodificación por palabra esté pendiente.

    Notes:
        El síndrome se calcula como H por la palabra columna en GF(2).
        La política para aplicar líderes de peso dos o más queda por definir.
    """
    raise NotImplementedError("Decodificación de canal por palabra pendiente.")


def decode_channel(
    received_bits: str,
    parity_check_matrix: np.ndarray,
    syndrome_table: SyndromeTable,
    *,
    source_bit_length: int,
) -> DecodedChannel:
    """Recupera los bits de fuente a partir de las palabras de canal recibidas.

    Args:
        received_bits: Cadena binaria demodulada, con el relleno de modulación
            ya retirado.
        parity_check_matrix: Matriz binaria H de forma (n-k, n).
        syndrome_table: Tabla completa de síndromes y líderes de coset de H.
        source_bit_length: Cantidad de bits Huffman antes del relleno de canal.

    Returns:
        Bits Huffman recortados a su longitud original, cantidad de bloques con
        síndrome no nulo y cantidad de bloques detectados sin corregir.
        Un flujo vacío con longitud original cero devuelve una cadena vacía
        y ambos conteos en cero.

    Raises:
        ValueError: Si el flujo contiene bits inválidos, la longitud original es
            negativa o la cantidad de bits recibidos difiere de n veces la
            cantidad de bloques necesaria para la longitud original.
        NotImplementedError: Mientras la decodificación por flujo esté pendiente.

    Notes:
        Deduce n y k de la forma de H. Procesa cada bloque con
        decode_channel_word, concatena los últimos k bits de cada palabra
        resultante y retira el relleno de canal al final.
    """
    raise NotImplementedError("Decodificación de canal por flujo pendiente.")
