"""Prueba las funciones de codificacion y decodificacion de canal.

Ejecutar desde la raiz del proyecto:
    python -m experiments.codificacion_canal
"""

import numpy as np

from common.channel_code import (
    build_parity_check_matrix,
    build_syndrome_table,
    calculate_channel_code_parameters,
)
from common.data_types import EncodedSource
from common.report_utils import print_syndrome_table
from config import GROUP_4_CHANNEL_CODE
from receiver.channel_decoder import decode_channel, decode_channel_word
from transmitter.channel_encoder import encode_channel, encode_channel_word


def run_experiment() -> None:
    """Ejecuta comprobaciones del codigo de canal del grupo 4."""
    code = GROUP_4_CHANNEL_CODE
    parity_check_matrix = build_parity_check_matrix(code)
    syndrome_table = build_syndrome_table(parity_check_matrix)

    print(parity_check_matrix)
    print("\n##########\n")
    print_syndrome_table(syndrome_table)

    parameters = calculate_channel_code_parameters(code)

    print(f"\n##########\n")
    print(f"dmin: {parameters.minimum_distance}")
    print(f"Errores detectables: {parameters.detectable_errors}")
    print(f"t: {parameters.correctable_errors}")

    #corrobora dimensiones y propiedades de las matrices y tablas generadas
    assert parity_check_matrix.shape == (code.n - code.k, code.n)
    assert np.array_equal(
        (code.generator_matrix @ parity_check_matrix.T) % 2,
        np.zeros((code.k, code.n - code.k), dtype=np.int64),
    )
    assert len(syndrome_table) == 2 ** (code.n - code.k)
    assert parameters.minimum_distance == 3
    assert parameters.detectable_errors == 2
    assert parameters.correctable_errors == 1
    print(
        "Funciones de channel_code.py: OK "
        f"(H={parity_check_matrix.shape}, "
        f"{len(syndrome_table)} sindromes, parametros={parameters})"
    )

    checked_errors = 0
    for value in range(2**code.k):
        #Crea todas las palabras de código posibles a partir de los mensajes de k bits, codifica y decodifica, y verifica que se corrigen los errores de un bit
        #En cada una de las 16 palabras prueba corregir los 10 errores de un bit posibles, se realizan 160 verificaciones
        message = format(value, f"0{code.k}b")
        codeword = encode_channel_word(message, code)
        decoded = decode_channel_word(codeword, parity_check_matrix, syndrome_table)
        assert decoded.corrected_word == codeword
        assert decoded.syndrome == "0" * (code.n - code.k)

        for bit_index in range(code.n):
            received = list(codeword)
            received[bit_index] = "1" if received[bit_index] == "0" else "0"
            corrected = decode_channel_word(
                "".join(received), parity_check_matrix, syndrome_table
            )
            assert corrected.corrected_word == codeword
            assert corrected.syndrome != "0" * (code.n - code.k)
            checked_errors += 1

    print(
        f"encode_channel_word/decode_channel_word: OK "
        f"({2**code.k} palabras, {checked_errors} errores de un bit corregidos)"
    )

    # Prueba de codificación y decodificación de flujo de bits con relleno y un error
    source_bits = "10110110101"
    encoded = encode_channel(EncodedSource(bits=source_bits), code)
    assert encoded.source_bit_length == len(source_bits)
    assert len(encoded.bits) == 3 * code.n

    decoded_clean = decode_channel(
        encoded.bits,
        parity_check_matrix,
        syndrome_table,
        source_bit_length=encoded.source_bit_length,
    )
    assert decoded_clean.source.bits == source_bits
    assert decoded_clean.detected_blocks == 0
    assert decoded_clean.uncorrected_blocks == 0

    received_bits = list(encoded.bits)
    error_index = code.n + 2
    received_bits[error_index] = "1" if received_bits[error_index] == "0" else "0"
    decoded_with_error = decode_channel(
        "".join(received_bits),
        parity_check_matrix,
        syndrome_table,
        source_bit_length=encoded.source_bit_length,
    )
    assert decoded_with_error.source.bits == source_bits
    assert decoded_with_error.detected_blocks == 1
    assert decoded_with_error.uncorrected_blocks == 0

    #prueba la secuencia vacía, que debe codificarse a flujo vacío y decodificarse a fuente vacía
    empty_encoded = encode_channel(EncodedSource(bits=""), code)
    empty_decoded = decode_channel(
        empty_encoded.bits,
        parity_check_matrix,
        syndrome_table,
        source_bit_length=empty_encoded.source_bit_length,
    )
    assert empty_encoded.bits == ""
    assert empty_decoded.source.bits == ""
    assert empty_decoded.detected_blocks == 0

    print(
        "encode_channel/decode_channel: OK "
        f"(flujo de {len(source_bits)} bits con relleno, "
        "un error corregido y flujo vacio)"
    )
    print("Todas las comprobaciones finalizaron correctamente.")


if __name__ == "__main__":
    run_experiment()
