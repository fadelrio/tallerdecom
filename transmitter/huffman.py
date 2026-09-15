"""Contratos para construir y analizar el código Huffman."""

from common.data_types import HuffmanResult
from dataclasses import dataclass
import heapq

@dataclass
class _Node:
    probability: float
    symbol: int | None = None
    left: "_Node | None" = None
    right: "_Node | None" = None

    @property
    def is_leaf(self) -> bool:
        return self.symbol is not None


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
    """Construye un código Huffman de mínima varianza."""

    if not isinstance(probabilities, dict):
        raise TypeError("probabilities debe ser un diccionario.")

    if len(probabilities) == 0:
        raise ValueError("La fuente no puede estar vacía.")

    if any(p < 0 for p in probabilities.values()):
        raise ValueError("Las probabilidades deben ser no negativas.")

    total = sum(probabilities.values())
    if total <= 0:
        raise ValueError("La suma de probabilidades debe ser positiva.")

    # Caso especial: un único símbolo.
    if len(probabilities) == 1:
        symbol = next(iter(probabilities))
        codebook = {symbol: "0"}

        stats = CodeStatistics(
            minimum_length=1,
            average_length=1.0,
            variance=0.0,
            is_prefix_code=True,
        )

        return HuffmanResult(codebook=codebook, statistics=stats)

    heap = []
    order = 0

    # Inserción inicial.
    for symbol, p in sorted(probabilities.items()):
        heapq.heappush(heap, (p, order, _Node(probability=p, symbol=symbol)))
        order += 1

    # Construcción del árbol.
    while len(heap) > 1:
        p1, _, left = heapq.heappop(heap)
        p2, _, right = heapq.heappop(heap)

        parent = _Node(
            probability=p1 + p2,
            left=left,
            right=right,
        )

        # El nuevo nodo queda detrás de todos los existentes.
        heapq.heappush(heap, (parent.probability, order, parent))
        order += 1

    root = heap[0][2]

    codebook = {}

    def assign_codes(node: _Node, prefix: str):
        if node.is_leaf:
            codebook[node.symbol] = prefix
            return

        assign_codes(node.left, prefix + "0")
        assign_codes(node.right, prefix + "1")

    assign_codes(root, "")

    lengths = {
        symbol: len(code)
        for symbol, code in codebook.items()
    }

    minimum_length = min(lengths.values())

    average_length = sum(
        probabilities[s] * lengths[s]
        for s in probabilities
    )

    variance = sum(
        probabilities[s] * (lengths[s] - average_length) ** 2
        for s in probabilities
    )

    is_prefix_code = True
    codes = list(codebook.values())

    for i, c1 in enumerate(codes):
        for j, c2 in enumerate(codes):
            if i != j and c2.startswith(c1):
                is_prefix_code = False
                break
        if not is_prefix_code:
            break

    stats = CodeStatistics(
        minimum_length=minimum_length,
        average_length=average_length,
        variance=variance,
        is_prefix_code=is_prefix_code,
    )

    return HuffmanResult(
        codebook=codebook,
        statistics=stats,
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

    if entropy < 0:
        raise ValueError("La entropía no puede ser negativa.")

    if average_length <= 0:
        raise ValueError("La longitud promedio debe ser mayor que cero.")

    return entropy / average_length
    