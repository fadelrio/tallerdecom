"""Contratos de gráficos; no importan Matplotlib ni generan imágenes todavía."""

from pathlib import Path

from common.data_types import Constellation, SymbolStatistics


def plot_constellation(constellation: Constellation, output_file: Path) -> None:
    """Guardará una constelación con etiquetas y regiones de decisión.

    Args:
        constellation: Coordenadas y etiquetas comunes del sistema.
        output_file: Ruta PNG; el directorio padre debe existir.

    Returns:
        None; el resultado futuro será el archivo indicado.

    Raises:
        NotImplementedError: Mientras el gráfico esté pendiente.
        ValueError: En la futura implementación, para datos incompatibles.

    Notes:
        Para FSK de dimensión mayor que tres, identificar explícitamente la
        proyección o representación utilizada y sus límites para visualizar
        regiones. No confundirla con la constelación completa. No abrir ventanas.
        Matplotlib será una dependencia futura al implementar este módulo.
    """
    raise NotImplementedError("Gráfico de constelación pendiente.")


def plot_symbol_histogram(
    statistics: SymbolStatistics, output_file: Path,
) -> None:
    """Guardará cantidades y frecuencias por símbolo de modulación.

    Args:
        statistics: Etiquetas, conteos y probabilidades ya preparados.
        output_file: Ruta PNG; el directorio padre debe existir.

    Returns:
        None; el resultado futuro será el archivo indicado.

    Raises:
        NotImplementedError: Mientras el gráfico esté pendiente.
        ValueError: En la futura implementación, para datos incompatibles.

    Notes:
        Presentar ambas magnitudes sin volver a calcularlas ni concluir que
        la fuente es equiprobable. No abrir ventanas interactivas.
    """
    raise NotImplementedError("Gráfico de histograma pendiente.")
