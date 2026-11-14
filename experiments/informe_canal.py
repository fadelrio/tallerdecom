"""Imprime las matrices, parámetros y un ejemplo de corrección del canal.

Ejecutar desde la raíz del proyecto:
    python -m experiments.informe_canal
"""

from common.channel_code import (
    build_parity_check_matrix,
    build_syndrome_table,
    calculate_channel_code_parameters,
)
from common.report_utils import print_syndrome_table
from config import GROUP_4_CHANNEL_CODE
from receiver.channel_decoder import decode_channel_word
from transmitter.channel_encoder import encode_channel_word


def run_report() -> None:
    """Muestra el informe del código de canal configurado para el grupo 4."""
    code = GROUP_4_CHANNEL_CODE
    parity_check_matrix = build_parity_check_matrix(code)
    syndrome_table = build_syndrome_table(parity_check_matrix)
    parameters = calculate_channel_code_parameters(code)

    print("1) Matriz generadora y parametros")
    print("G =")
    print(code.generator_matrix)
    print(f"n = {code.n}")
    print(f"k = {code.k}")
    print(f"r = k/n = {code.k}/{code.n} = {code.k / code.n:.4f}")

    print("\n2) Matriz de chequeo de paridad H")
    print("H =")
    print(parity_check_matrix)

    print("\n3) Distancia minima y capacidades")
    print(f"d_min = {parameters.minimum_distance}")
    print(f"e = {parameters.detectable_errors} errores detectables")
    print(f"t = {parameters.correctable_errors} errores corregibles")

    print("\n4) Tabla de sindromes")
    print_syndrome_table(syndrome_table)

    message = "1011"
    codeword = encode_channel_word(message, code)
    error_position = 2
    error_mask = "".join(
        "1" if index == error_position else "0"
        for index in range(code.n)
    )
    corrupted_word = "".join(
        str(int(bit) ^ int(error))
        for bit, error in zip(codeword, error_mask)
    )
    decoding = decode_channel_word(
        corrupted_word,
        parity_check_matrix,
        syndrome_table,
    )
    assert decoding.corrected_word == codeword
    assert decoding.applied_error == error_mask

    print("\n5) Ejemplo de deteccion y correccion")
    print(f"Mensaje: {message}")
    print(f"Palabra de codigo original: {codeword}")
    print(f"Error introducido:          {error_mask}")
    print(f"Palabra recibida:           {corrupted_word}")
    print(f"Sindrome recibido:          {decoding.syndrome}")
    print(f"Error aplicado:             {decoding.applied_error}")
    print(f"Palabra corregida:          {decoding.corrected_word}")


if __name__ == "__main__":
    run_report()


