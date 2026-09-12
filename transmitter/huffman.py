"""Contratos para construir y analizar el código Huffman."""

from common.data_types import HuffmanResult


def build_huffman_code(probabilities: dict[int, float]) -> HuffmanResult:
    """Construirá el código Huffman y calculará sus estadísticas.

    Args:
        probabilities: Probabilidades de los símbolos enteros entre 0 y 255.

    Returns:
        Diccionario de palabras binarias y estadísticas del código.

    Raises:
        NotImplementedError: La funcionalidad está pendiente.

    Notes:
        Deberá construir el árbol de Huffman, asignar palabras binarias y
        generar un código prefijo. También calculará la longitud mínima,
        la longitud promedio y la varianza ponderadas por las probabilidades,
        y verificará la propiedad de prefijo. Devolverá un HuffmanResult.
    """
    raise NotImplementedError(
        "Construcción y estadísticas de Huffman pendientes."
    )


def calculate_efficiency(entropy: float, average_length: float) -> float:
    """Calculará la eficiencia del código como eta = H(X) / L_promedio.

    Args:
        entropy: Entropía de la fuente en bits por símbolo.
        average_length: Longitud promedio del código en bits por símbolo.

    Returns:
        Eficiencia adimensional como fracción, sin conversión a porcentaje.

    Raises:
        NotImplementedError: La funcionalidad está pendiente.

    Notes:
        La conversión a porcentaje pertenece a la presentación.
    """
    raise NotImplementedError("Cálculo de eficiencia pendiente.")
