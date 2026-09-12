"""Contrato para el análisis estadístico y la entropía de la fuente."""

from common.data_types import SourceStatistics


def analyze_source(data: bytes) -> SourceStatistics:
    """Analizará estadísticamente una fuente binaria.

    Args:
        data: Bytes del archivo de entrada, incluidos los no imprimibles.

    Returns:
        Conteos, probabilidades, cantidad total y entropía en bits por símbolo.

    Raises:
        NotImplementedError: La funcionalidad está pendiente.

    Notes:
        Deberá recorrer los bytes, contar cada símbolo entero 0..255,
        calcular sus probabilidades y la entropía y devolver SourceStatistics.
        Todavía no se realiza ninguno de esos cálculos.
    """
    raise NotImplementedError("Análisis estadístico de fuente pendiente.")
