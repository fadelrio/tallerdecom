"""Contratos para la matriz de paridad y los parámetros del código de canal."""

import numpy as np

from common.data_types import ChannelCodeConfig, ChannelCodeParameters, SyndromeTable

# Función de validación de la matriz generadora G (es por si G no fuera una matriz de numpy). Es sólo una protección.
def _binary_generator_matrix(code: ChannelCodeConfig) -> np.ndarray:
    """Devuelve G como matriz entera, verificando su forma (k, n) y sus valores."""
    generator = np.asarray(code.generator_matrix, dtype=np.int64)

    if generator.shape != (code.k, code.n):
        raise ValueError(
            f"G debe tener forma ({code.k}, {code.n}) y tiene {generator.shape}."
        )

    if not np.isin(generator, (0, 1)).all():
        raise ValueError("G solo puede contener los valores 0 y 1.")

    return generator


def build_parity_check_matrix(code: ChannelCodeConfig) -> np.ndarray:
    """Obtiene la matriz de chequeo de paridad del código sistemático.

    Args:
        code: Parámetros n y k y matriz binaria G = [P | I_k].

    Returns:
        Matriz binaria H = [I_(n-k) | P transpuesta] de forma (n-k, n).

    Raises:
        ValueError: Si G no tiene forma (k, n), no es binaria o no tiene
            la identidad I_k en sus últimas k columnas.

    Notes:
        El producto G por la transpuesta de H es cero en GF(2).
        En GF(2) no hace falta cambiar el signo de P: -P = P.
    """
    generator = _binary_generator_matrix(code)
    k, n = code.k, code.n

    # G = [P | I_k]: P son las primeras n-k columnas, I_k las últimas k.
    parity_part = generator[:, : n - k]
    identity_part = generator[:, n - k :]

    if not np.array_equal(identity_part, np.eye(k, dtype=np.int64)):
        raise ValueError("G debe ser sistemática: I_k en las últimas k columnas.")

    # H = [I_(n-k) | P transpuesta], de forma (n-k, n).
    return np.hstack([np.eye(n - k, dtype=np.int64), parity_part.T])


def build_syndrome_table(parity_check_matrix: np.ndarray) -> SyndromeTable:
    """Asocia cada síndrome posible con su líder de coset.

    Args:
        parity_check_matrix: Matriz binaria H de forma (n-k, n).

    Returns:
        Tabla de 2**(n-k) entradas. Cada clave tiene n-k bits y cada máscara
        tiene n bits. Para el grupo 4 hay 64 entradas.

    Raises:
        ValueError: Si H no es una matriz bidimensional de ceros y unos.

    Notes:
        Los bits del síndrome siguen el orden de las filas de H. Para cada
        síndrome se elige el patrón de peso mínimo y, en caso de empate,
        la máscara lexicográficamente menor. El síndrome cero tiene máscara cero.
        Se recorren todos los patrones de error de n bits ordenados por peso
        y, a igual peso, por valor (que coincide con el orden lexicográfico
        de las cadenas); el primero que produce cada síndrome es su líder.
    """
    parity = np.asarray(parity_check_matrix, dtype=np.int64)

    if parity.ndim != 2 or not np.isin(parity, (0, 1)).all():
        raise ValueError("H debe ser una matriz bidimensional de ceros y unos.")

    redundancy, n = parity.shape
    total_syndromes = 2**redundancy

    # Patrones de error como enteros de n bits, de menor a mayor peso.
    patterns = sorted(range(2**n), key=lambda value: (bin(value).count("1"), value))

    table: SyndromeTable = {}

    for value in patterns:
        mask = format(value, f"0{n}b")
        error = np.array([int(bit) for bit in mask], dtype=np.int64)

        # Síndrome s = H e^T en GF(2); un bit por cada fila de H.
        syndrome = "".join(str(bit) for bit in (parity @ error) % 2)

        if syndrome not in table:
            table[syndrome] = mask

            if len(table) == total_syndromes:
                break

    return table


def calculate_channel_code_parameters(code: ChannelCodeConfig) -> ChannelCodeParameters:
    """Calcula la distancia mínima y las capacidades garantizadas del código.

    Args:
        code: Parámetros del código lineal y su matriz generadora binaria.

    Returns:
        Distancia mínima d_min, capacidad de detección d_min - 1 y capacidad
        de corrección (d_min - 1) // 2, expresadas en bits por palabra.

    Raises:
        ValueError: Si G no tiene forma (k, n) o no es binaria.

    Notes:
        La distancia mínima de un código lineal es el menor peso de Hamming
        entre sus palabras no nulas. Para el grupo 4 se espera (3, 2, 1).
        Se generan las 2**k - 1 palabras asociadas a los mensajes no nulos.
    """
    generator = _binary_generator_matrix(code)
    k = code.k

    # Todos los mensajes no nulos de k bits, uno por fila.
    values = np.arange(1, 2**k)
    messages = (values[:, None] >> np.arange(k - 1, -1, -1)) & 1

    codewords = (messages @ generator) % 2
    minimum_distance = int(codewords.sum(axis=1).min())

    return ChannelCodeParameters(
        minimum_distance=minimum_distance,
        detectable_errors=minimum_distance - 1,
        correctable_errors=(minimum_distance - 1) // 2,
    )