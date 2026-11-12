"""Contratos para la matriz de paridad y los parámetros del código de canal."""

import numpy as np

from common.data_types import ChannelCodeConfig, ChannelCodeParameters, SyndromeTable


def build_parity_check_matrix(code: ChannelCodeConfig) -> np.ndarray:
    """Obtiene la matriz de chequeo de paridad del código sistemático.

    Args:
        code: Parámetros n y k y matriz binaria G = [P | I_k].

    Returns:
        Matriz binaria H = [I_(n-k) | P transpuesta] de forma (n-k, n).

    Raises:
        NotImplementedError: Mientras la construcción de H esté pendiente.

    Notes:
        El producto G por la transpuesta de H es cero en GF(2).
    """
    raise NotImplementedError("Construcción de la matriz de paridad pendiente.")


def build_syndrome_table(parity_check_matrix: np.ndarray) -> SyndromeTable:
    """Asocia cada síndrome posible con su líder de coset.

    Args:
        parity_check_matrix: Matriz binaria H de forma (n-k, n).

    Returns:
        Tabla de 2**(n-k) entradas. Cada clave tiene n-k bits y cada máscara
        tiene n bits. Para el grupo 4 hay 64 entradas.

    Raises:
        NotImplementedError: Mientras la construcción de la tabla esté pendiente.

    Notes:
        Los bits del síndrome siguen el orden de las filas de H. Para cada
        síndrome se elige el patrón de peso mínimo y, en caso de empate,
        la máscara lexicográficamente menor. El síndrome cero tiene máscara cero.
    """
    raise NotImplementedError("Construcción de la tabla de síndromes pendiente.")


def calculate_channel_code_parameters(code: ChannelCodeConfig) -> ChannelCodeParameters:
    """Calcula la distancia mínima y las capacidades garantizadas del código.

    Args:
        code: Parámetros del código lineal y su matriz generadora binaria.

    Returns:
        Distancia mínima d_min, capacidad de detección d_min - 1 y capacidad
        de corrección (d_min - 1) // 2, expresadas en bits por palabra.

    Raises:
        NotImplementedError: Mientras el cálculo de los parámetros esté pendiente.

    Notes:
        La distancia mínima de un código lineal es el menor peso de Hamming
        entre sus palabras no nulas. Para el grupo 4 se espera (3, 2, 1).
    """
    raise NotImplementedError("Cálculo de los parámetros del código pendiente.")
