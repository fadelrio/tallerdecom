"""Análisis estadístico y entropía de la fuente."""

import math
from collections import Counter

from common.data_types import SourceStatistics


def calculate_entropy(probabilities: dict[int, float]) -> float:
    """Calcula la entropía H(X) del texto a partir de sus probabilidades.

    Args:
        probabilities: Probabilidad de ocurrencia de cada símbolo entero
            (0..255), ya calculadas sobre el texto ingresado.

    Returns:
        Entropía en bits por símbolo: H(X) = -sum(p_i * log2(p_i)).

    Notes:
        Solo se suma sobre símbolos con probabilidad > 0 (los que realmente
        aparecieron en el texto), evitando log2(0). Si no hay símbolos
        (diccionario vacío), la entropía es 0.0: sin ocurrencias no hay
        incertidumbre que medir.
    """
    if not probabilities:
        return 0.0

    return -sum(p * math.log2(p) for p in probabilities.values())


def analyze_source(data: bytes) -> SourceStatistics:
    """Analiza estadísticamente una fuente binaria.

    Args:
        data: Bytes del archivo de entrada, incluidos los no imprimibles.

    Returns:
        Conteos, probabilidades, cantidad total y entropía en bits por símbolo.

    Notes:
        Recorre los bytes una sola vez con `collections.Counter`, que ya
        trata cada byte como un entero 0..255 (letras, dígitos, caracteres
        especiales y de control quedan cubiertos por igual, sin distinción
        de categoría). Las probabilidades se calculan como frecuencia
        relativa (conteo / total) y la entropía se delega a
        `calculate_entropy`, que implementa H(X) = -sum(p_i * log2(p_i))
        sobre las probabilidades ya calculadas (punto 2 del enunciado).

        Caso de fuente vacía: se define como total_symbols = 0,
        counts y probabilities vacíos, y entropía 0.0 (no hay incertidumbre
        sin símbolos). Caso de símbolo único: probabilidad 1.0 para ese
        símbolo y entropía 0.0, consistente con H(X) = 0 cuando no hay
        incertidumbre en la fuente.
    """
    total_symbols = len(data)

    if total_symbols == 0:
        return SourceStatistics(
            counts={},
            probabilities={},
            total_symbols=0,
            entropy=0.0,
        )

    counts = dict(Counter(data))

    probabilities = {
        symbol: count / total_symbols for symbol, count in counts.items()
    }

    entropy = calculate_entropy(probabilities)

    return SourceStatistics(
        counts=counts,
        probabilities=probabilities,
        total_symbols=total_symbols,
        entropy=entropy,
    )