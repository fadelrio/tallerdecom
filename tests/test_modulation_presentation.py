"""Contratos de salida del informe y los gráficos con datos manuales."""

from pathlib import Path

import numpy as np
import pytest

from common.data_types import Constellation, EnergyStatistics, ErrorRates, SymbolStatistics
from common.modulation_plots import plot_constellation, plot_symbol_histogram
from common.modulation_report import format_modulation_report
from config import ModulationConfig
from tests._pending import available


def test_modulation_report_data() -> None:
    """El Markdown debe distinguir referencias y mediciones sin recalcularlas."""
    statistics = SymbolStatistics(["00", "01", "11", "10"], np.array([3, 0, 1, 0]), np.array([0.75, 0.0, 0.25, 0.0]))
    output = format_modulation_report(
        ModulationConfig(4, "PAM"),
        EnergyStatistics(2.0, 1.0, 1.0), EnergyStatistics(2.5, 1.25, 1.25),
        ErrorRates(0.125, 0.0625), ErrorRates(0.25, 0.125), statistics,
    )
    assert isinstance(output, str)
    for text in ("PAM", "4", "gray", "Es", "Ec", "Eb", "SER", "BER", "2.5", "1.25", "0.0625", "0.75"):
        assert text in output
    assert "teóric" in output.lower() and "estimad" in output.lower()
    for label in statistics.labels:
        assert label in output


def test_report_preserves_supplied_values_and_zero_counts() -> None:
    """No fuerza referencias nominales ni elimina símbolos ausentes."""
    output = format_modulation_report(
        ModulationConfig(2, "FSK", labeling="binary", code_rate=0.5),
        EnergyStatistics(9.0, 8.0, 7.0), EnergyStatistics(6.0, 5.0, 4.0),
        ErrorRates(0.125, 0.0625), ErrorRates(0.0, 0.0),
        SymbolStatistics(["0", "1"], np.array([3, 0]), np.array([1.0, 0.0])),
    )
    assert "| Es (símbolo de modulación) | 9 | 6 |" in output
    assert "| Ec (bit de canal) | 8 | 5 |" in output
    assert "| Eb (bit de información) | 7 | 4 |" in output
    assert "| SER | 0.125 | 0 |" in output
    assert "| BER | 0.0625 | 0 |" in output
    assert "| 1 | 0 | 0 |" in output
    assert "FSK" in output and "binary" in output
    assert "Tasa de código k/n: 0.5" in output


def test_report_escapes_table_labels() -> None:
    """Una etiqueta malformada de presentación no rompe el Markdown."""
    output = format_modulation_report(
        ModulationConfig(2, "PAM"), EnergyStatistics(1.0, 1.0, 1.0),
        EnergyStatistics(1.0, 1.0, 1.0), ErrorRates(0.0, 0.0), ErrorRates(0.0, 0.0),
        SymbolStatistics(["|`<\n", "1"], np.array([1, 0]), np.array([1.0, 0.0])),
    )
    assert "&#124;&#96;&lt;&#10;" in output
    row = next(line for line in output.splitlines() if "&#124;" in line)
    assert row.count("|") == 4


@pytest.mark.parametrize("counts,probabilities", [([1], [0.5, 0.5]), ([1, 1], [0.5])])
def test_report_rejects_misaligned_histogram(counts: list[int], probabilities: list[float]) -> None:
    """No descarta silenciosamente filas al emparejar el histograma."""
    with pytest.raises(ValueError):
        format_modulation_report(
            ModulationConfig(2, "PAM"), EnergyStatistics(1.0, 1.0, 1.0),
            EnergyStatistics(1.0, 1.0, 1.0), ErrorRates(0.0, 0.0), ErrorRates(0.0, 0.0),
            SymbolStatistics(["0", "1"], np.array(counts), np.array(probabilities)),
        )


@pytest.mark.parametrize("kind", ["pam", "fsk", "histogram"])
def test_plot_creates_png(kind: str, tmp_path: Path) -> None:
    """La futura presentación guardará un PNG válido sin ventanas interactivas."""
    path = tmp_path / f"{kind}.png"
    if kind == "histogram":
        statistics = SymbolStatistics(["0", "1"], np.array([3, 1]), np.array([0.75, 0.25]))
        result = available(plot_symbol_histogram, statistics, path)
    else:
        symbols = np.array([[-1.0], [1.0]]) if kind == "pam" else np.eye(4)
        labels = ["0", "1"] if kind == "pam" else ["00", "01", "11", "10"]
        result = available(plot_constellation, Constellation(symbols, labels), path)
    assert result is None
    data = path.read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    assert int.from_bytes(data[16:20], "big") > 0
    assert int.from_bytes(data[20:24], "big") > 0
