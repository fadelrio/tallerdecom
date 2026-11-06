"""Constelaciones compartidas por el transmisor y el receptor."""

from math import sqrt

import numpy as np

from common.data_types import Constellation
from config import ModulationConfig, validate_modulation_config


def build_constellation(config: ModulationConfig) -> Constellation:
    """Construye las coordenadas y etiquetas del esquema seleccionado.

    Args:
        config: Configuración PAM/FSK, orden, Eb, etiquetamiento y tasa.

    Returns:
        Coordenadas (M, 1) para PAM o (M, M) para FSK ortogonal coherente,
        con una etiqueta de log2(M) bits por fila. Los niveles PAM estarán
        ordenados de menor a mayor y los símbolos FSK por eje de la base.

    Raises:
        TypeError: Si los parámetros tienen tipos incompatibles.
        ValueError: Si los parámetros están fuera de los valores admitidos.

    Notes:
        Para símbolos equiprobables, Es = log2(M) * Eb * code_rate.
    """
    validate_modulation_config(config)
    order = int(config.M)
    bits_per_symbol = order.bit_length() - 1
    symbol_rms = sqrt(config.Eb) * sqrt(bits_per_symbol * config.code_rate)

    if config.tipo == "PAM":
        levels = 2 * np.arange(order) - (order - 1)
        symbols = (levels * (symbol_rms * sqrt(3 / (order**2 - 1))))[:, None]
    else:
        symbols = np.eye(order) * symbol_rms

    indices = range(order)
    if config.labeling == "gray":
        labels = [format(i ^ (i >> 1), f"0{bits_per_symbol}b") for i in indices]
    else:
        labels = [format(i, f"0{bits_per_symbol}b") for i in indices]
    return Constellation(symbols, labels)
