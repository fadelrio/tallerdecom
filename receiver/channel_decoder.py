"""Contratos de decodificación de canal mediante síndromes."""

import numpy as np

from common.data_types import ChannelWordDecoding, DecodedChannel, SyndromeTable, EncodedSource


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
    
    # Validar que la palabra contenga solamente bits.
    if not all(bit in "01" for bit in received_word):
        raise ValueError("La palabra recibida debe contener solamente bits.")

    H = np.asarray(parity_check_matrix)

    # Validar la matriz de control.
    if H.ndim != 2 or H.shape[0] == 0 or H.shape[1] == 0:
        raise ValueError("La matriz H debe ser bidimensional y no vacía.")

    if not np.all(np.isin(H, [0, 1])):
        raise ValueError("La matriz H debe ser binaria.")

    n = H.shape[1]

    if len(received_word) != n:
        raise ValueError("La longitud de la palabra no coincide con H.")

    # Convertir la palabra recibida a un vector NumPy.
    received = np.array([int(bit) for bit in received_word])

    # Calcular el síndrome en GF(2).
    syndrome_vector = (H @ received) % 2
    syndrome = "".join(str(bit) for bit in syndrome_vector)

    # Si el síndrome es cero, no se detectaron errores.
    if syndrome == "0" * H.shape[0]:
        applied_error = "0" * n
        corrected_word = received_word

    else:
        # Buscar el líder de coset asociado al síndrome.
        if syndrome not in syndrome_table:
            raise ValueError("El síndrome no se encuentra en la tabla.")

        applied_error = syndrome_table[syndrome]

        if (
            len(applied_error) != n
            or not all(bit in "01" for bit in applied_error)
        ):
            raise ValueError("La máscara de error de la tabla no es válida.")

        # Aplicar la máscara mediante XOR.
        error_vector = np.array([int(bit) for bit in applied_error])
        corrected = received ^ error_vector

        corrected_word = "".join(str(bit) for bit in corrected)

    return ChannelWordDecoding(
        corrected_word=corrected_word,
        syndrome=syndrome,
        applied_error=applied_error,
    )

    


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

    # Validar el flujo recibido.
    if not isinstance(received_bits, str) or not all(
        bit in "01" for bit in received_bits
    ):
        raise ValueError("El flujo recibido debe contener solamente bits.")

    if not isinstance(source_bit_length, (int, np.integer)) or source_bit_length < 0:
        raise ValueError("La longitud original debe ser un entero no negativo.")

    # Validar la matriz H.
    H = np.asarray(parity_check_matrix)

    if H.ndim != 2 or H.shape[0] == 0 or H.shape[1] == 0:
        raise ValueError("La matriz H debe ser bidimensional y no vacía.")

    if not np.all(np.isin(H, [0, 1])):
        raise ValueError("La matriz H debe ser binaria.")

    n = H.shape[1]
    k = n - H.shape[0]

    if k <= 0:
        raise ValueError("La matriz H debe permitir un código con k positivo.")

    # Calcular la cantidad de bloques necesarios.
    num_blocks = (source_bit_length + k - 1) // k

    # Verificar la longitud del flujo recibido.
    if len(received_bits) != num_blocks * n:
        raise ValueError("La longitud del flujo recibido no es compatible con la fuente.")

    # Caso particular: fuente vacía.
    if num_blocks == 0:
        return DecodedChannel(
            source=EncodedSource(bits=""),
            detected_blocks=0,
            uncorrected_blocks=0,
        )

    recovered_bits = []
    detected_blocks = 0
    uncorrected_blocks = 0

    # Procesar cada palabra de canal.
    for i in range(num_blocks):
        received_word = received_bits[i * n:(i + 1) * n]

        result = decode_channel_word(
            received_word,
            H,
            syndrome_table,
        )

        # Contabilizar bloques con errores detectados.
        if result.syndrome != "0" * H.shape[0]:
            detected_blocks += 1

        # Contabilizar bloques detectados que quedaron sin corregir.
        if result.applied_error is None:
            uncorrected_blocks += 1

        # Extraer los k bits de información.
        recovered_bits.append(result.corrected_word[-k:])

    # Concatenar los bits recuperados.
    recovered_source = "".join(recovered_bits)

    # Eliminar el relleno de canal.
    recovered_source = recovered_source[:source_bit_length]

    return DecodedChannel(
        source=EncodedSource(bits=recovered_source),
        detected_blocks=detected_blocks,
        uncorrected_blocks=uncorrected_blocks,
    )
    
