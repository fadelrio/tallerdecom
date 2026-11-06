"""Gráficos de modulación para el informe."""

from pathlib import Path

import numpy as np

from common.data_types import Constellation, SymbolStatistics


def plot_constellation(
    constellation: Constellation, output_file: Path, *, received_symbols: np.ndarray | None = None,
) -> None:
    """Guarda una constelación con etiquetas y regiones de decisión.

    Args:
        constellation: Coordenadas y etiquetas comunes del sistema.
        output_file: Ruta PNG; el directorio padre debe existir.
        received_symbols: Muestras opcionales del canal en la misma base.

    Returns:
        None; el gráfico se escribe en el archivo indicado.

    Raises:
        ValueError: Para coordenadas o etiquetas incompatibles.

    Notes:
        En FSK de dimensión mayor que dos se muestra un corte ortonormal
        por el origen y se proyectan las muestras sobre ese plano.
    """
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from matplotlib.figure import Figure

    symbols = _coordinate_matrix(constellation.symbols)
    order, dimension = symbols.shape
    if order < 2 or order != len(constellation.labels):
        raise ValueError("Se requieren al menos dos símbolos con una etiqueta por fila.")
    if dimension == 1:
        if np.any(np.diff(symbols[:, 0]) <= 0):
            raise ValueError("Los niveles PAM deben ser estrictamente crecientes.")
    elif dimension != order or symbols[0, 0] <= 0 or not np.array_equal(
        symbols, np.eye(order) * symbols[0, 0],
    ):
        raise ValueError("FSK requiere un símbolo de igual amplitud positiva por eje.")

    received = None
    if received_symbols is not None:
        received = _coordinate_matrix(received_symbols)
        if received.shape[1] != dimension:
            raise ValueError("Las muestras deben tener la dimensión de la constelación.")

    figure = Figure(figsize=(8, 3 if dimension == 1 else 6), layout="constrained")
    FigureCanvasAgg(figure)
    axes = figure.subplots()
    if dimension == 1:
        levels = symbols[:, 0]
        points = np.column_stack((levels, np.zeros(order)))
        for threshold in levels[:-1] / 2 + levels[1:] / 2:
            axes.axvline(threshold, color="0.55", linestyle="--", linewidth=1)
        if received is not None:
            received = np.column_stack((received[:, 0], np.full(len(received), -0.2)))
        axes.set(title=f"{order}-PAM", xlabel="Coordenada en la base PAM", yticks=[], ylim=(-0.5, 0.5))
    else:
        points = symbols
        axes.set_aspect("equal")
        if dimension == 2:
            axes.axline((0, 0), slope=1, color="0.55", linestyle="--", linewidth=1)
            axes.set(title="2-FSK", xlabel="Eje 1", ylabel="Eje 2")
        else:
            angles = 2 * np.pi * np.arange(order) / order
            plane = np.sqrt(2 / order) * np.column_stack((np.cos(angles), np.sin(angles)))
            points = symbols @ plane
            if received is not None:
                received = received @ plane
            extent = np.max(np.abs(points))
            if received is not None and received.size:
                extent = max(extent, np.max(np.abs(received)))
            extent *= 1.2
            boundaries = angles + np.pi / order
            for angle in boundaries:
                ray = np.sqrt(2) * extent * np.array([np.cos(angle), np.sin(angle)])
                axes.plot([0, ray[0]], [0, ray[1]], color="0.55", linestyle="--", linewidth=1)
            axes.set(
                title=f"{order}-FSK · Corte ortonormal 2D por el origen",
                xlabel="Componente coseno · Regiones válidas en el plano del corte",
                ylabel="Componente seno",
                xlim=(-extent, extent), ylim=(-extent, extent),
            )

    if received is not None and received.size:
        axes.scatter(*received.T, s=12, alpha=0.3, color="tab:orange", label="Muestras recibidas")
    axes.scatter(*points.T, color="tab:blue", label="Símbolos ideales", zorder=3)
    label_offset = (0, 5) if dimension == 1 else (4, 5)
    label_alignment = "center" if dimension == 1 else "left"
    for point, label in zip(points, constellation.labels):
        axes.annotate(
            label, point, xytext=label_offset, textcoords="offset points",
            ha=label_alignment, fontsize=9,
        )
    if received is not None and received.size:
        axes.legend(loc="upper right")
    figure.savefig(output_file, format="png", dpi=140)


def _coordinate_matrix(values: np.ndarray) -> np.ndarray:
    coordinates = np.asarray(values)
    if coordinates.ndim != 2 or not (
        np.issubdtype(coordinates.dtype, np.integer) or np.issubdtype(coordinates.dtype, np.floating)
    ) or not np.isfinite(coordinates).all():
        raise ValueError("Las coordenadas deben formar una matriz real y finita.")
    return coordinates


def plot_symbol_histogram(
    statistics: SymbolStatistics, output_file: Path,
) -> None:
    """Guarda cantidades y frecuencias por símbolo de modulación.

    Args:
        statistics: Etiquetas, conteos y probabilidades ya preparados.
        output_file: Ruta PNG; el directorio padre debe existir.

    Returns:
        None; el gráfico se escribe en el archivo indicado.

    Raises:
        ValueError: Para etiquetas, cantidades o probabilidades incompatibles.

    Notes:
        Presentar ambas magnitudes sin volver a calcularlas ni concluir que
        la fuente es equiprobable. No abrir ventanas interactivas.
    """
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from matplotlib.figure import Figure
    from matplotlib.ticker import MaxNLocator

    labels = statistics.labels
    counts = np.asarray(statistics.counts)
    probabilities = np.asarray(statistics.probabilities)
    if (
        not labels or len(set(labels)) != len(labels)
        or counts.shape != (len(labels),) or probabilities.shape != counts.shape
        or counts.dtype.kind not in "iu" or (counts < 0).any()
        or probabilities.dtype.kind not in "iuf" or not np.isfinite(probabilities).all()
        or ((probabilities < 0) | (probabilities > 1)).any()
    ):
        raise ValueError("Los conteos y probabilidades deben ser válidos y coincidir con las etiquetas.")

    figure = Figure(figsize=(8, 6), layout="constrained")
    FigureCanvasAgg(figure)
    counts_axes, probabilities_axes = figure.subplots(2, 1, sharex=True)
    counts_axes.bar(labels, counts, color="tab:blue")
    counts_axes.set(title="Símbolos transmitidos", ylabel="Cantidad")
    counts_axes.yaxis.set_major_locator(MaxNLocator(integer=True))
    probabilities_axes.bar(labels, probabilities, color="tab:blue")
    probabilities_axes.axhline(
        1 / len(labels), color="0.35", linestyle="--", label="Referencia equiprobable (1/M)",
    )
    probabilities_axes.set(xlabel="Etiqueta del símbolo", ylabel="Frecuencia relativa")
    probabilities_axes.legend()
    figure.savefig(output_file, format="png", dpi=140)
