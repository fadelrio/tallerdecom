"""Contratos para preparar datos del informe sin generar documentos."""

from common.data_types import (
    CodingReport,
    EncodedSource,
    HuffmanResult,
    SourceReport,
    SourceStatistics,
)


def build_source_table(
    statistics: SourceStatistics,
    huffman: HuffmanResult,
) -> list[SourceReport]:
    """Preparará la tabla de símbolos del informe B.

    Args:
        statistics: Conteos y probabilidades de la fuente.
        huffman: Código Huffman de los símbolos observados.

    Returns:
        Una fila por símbolo con su carácter Unicode, cantidad, probabilidad
        y palabra Huffman.

    Raises:
        NotImplementedError: La preparación de la tabla está pendiente.

    Notes:
        La representación legible de caracteres de control corresponde a una
        futura capa de presentación; no modifica los símbolos internos.
    """
    raise NotImplementedError("Tabla de símbolos pendiente.")


def build_coding_report(
    statistics: SourceStatistics,
    huffman: HuffmanResult,
    encoded: EncodedSource,
) -> CodingReport:
    """Preparará las métricas comparativas del informe B.

    Args:
        statistics: Entropía y cantidad total de símbolos de la fuente.
        huffman: Código y estadísticas de sus longitudes.
        encoded: Secuencia codificada cuya longitud dará el total de bits.

    Returns:
        Entropía, longitud mínima y promedio, varianza, eficiencia como
        fracción, longitud fija de 8 bits y totales de bits Huffman y fijo.

    Raises:
        NotImplementedError: La preparación del informe está pendiente.

    Notes:
        Deberá utilizar calculate_efficiency para la eficiencia. El total
        fijo será 8 por la cantidad de símbolos; el total Huffman será la
        longitud de encoded.bits. No generará PDF, Word ni otros documentos.
    """
    raise NotImplementedError("Datos comparativos del informe pendientes.")

def print_source(stats: SourceStatistics) -> None:
    """Imprime conteos y probabilidades por carácter.

    Args:
        stats: Estadísticas de la fuente textual.
    """
    print("Carácter | Cantidad | Probabilidad")
    for symbol in sorted(stats.counts):
        print(f"{symbol!r} | {stats.counts[symbol]} | "
              f"{stats.probabilities[symbol]:.4f}")
    print(f"Total de caracteres: {stats.total_symbols}")
    print(f"Entropía: {stats.entropy:.4f} bits/carácter")


def print_huffman(result: HuffmanResult) -> None:
    """Imprime palabras Huffman y métricas, escapando controles.

    Args:
        result: Código y estadísticas calculadas.
    """
    for symbol, word in sorted(result.codebook.items()):
        print(f"{symbol!r}: {word}")
    stats = result.statistics
    print(f"Largo promedio mínimo teórico: {stats.minimum_length}")
    print(f"Largo promedio: {stats.average_length}")
    print(f"Varianza: {stats.variance}")
    print(f"Código prefijo: {stats.is_prefix_code}")
