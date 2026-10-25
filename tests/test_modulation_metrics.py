"""Referencias manuales de energías, errores e histograma para implementar luego."""

import numpy as np
import pytest

from common.data_types import Constellation, EnergyStatistics, ModulatedData
from common.modulation_metrics import (
    estimate_bit_error_rate, estimate_energies, estimate_symbol_error_rate,
    symbol_statistics, theoretical_energies, theoretical_error_rates,
)
from config import ModulationConfig
from tests._pending import available


@pytest.mark.parametrize("tipo", ["PAM", "FSK"])
@pytest.mark.parametrize("M,rate,expected", [
    (2, 1.0, EnergyStatistics(1.0, 1.0, 1.0)),
    (4, 1.0, EnergyStatistics(2.0, 1.0, 1.0)),
    (8, 1.0, EnergyStatistics(3.0, 1.0, 1.0)),
    (16, 1.0, EnergyStatistics(4.0, 1.0, 1.0)),
    (2, 0.5, EnergyStatistics(0.5, 0.5, 1.0)),
    (4, 0.5, EnergyStatistics(1.0, 0.5, 1.0)),
    (8, 0.5, EnergyStatistics(1.5, 0.5, 1.0)),
    (16, 0.5, EnergyStatistics(2.0, 0.5, 1.0)),
])
def test_theoretical_energy_reference(tipo: str, M: int, rate: float, expected: EnergyStatistics) -> None:
    """Distingue símbolo, bit de canal y bit de información para cada orden."""
    result = available(theoretical_energies, ModulationConfig(M, tipo, code_rate=rate))
    assert result == expected


@pytest.mark.parametrize("tipo,symbols,rate,expected", [
    ("PAM", [[-1.0], [3.0]], 1.0, EnergyStatistics(5.0, 5.0, 5.0)),
    ("PAM", [[-1.0], [3.0]], 0.5, EnergyStatistics(5.0, 5.0, 10.0)),
    ("FSK", [[1.0, 0.0], [0.0, 2.0]], 1.0, EnergyStatistics(2.5, 2.5, 2.5)),
])
def test_estimated_energy(tipo: str, symbols: list[list[float]], rate: float, expected: EnergyStatistics) -> None:
    """La energía se mide en la muestra, sin forzar el valor nominal Eb=1."""
    result = available(estimate_energies, np.array(symbols), ModulationConfig(2, tipo, code_rate=rate))
    assert result == expected


@pytest.mark.parametrize("symbols", [np.empty((0, 1)), np.array([1.0, 2.0]), np.array([[float("nan")]])])
def test_invalid_energy_sample(symbols: np.ndarray) -> None:
    """No se estima una energía con datos vacíos, no finitos o sin matriz."""
    with pytest.raises(ValueError):
        available(estimate_energies, symbols, ModulationConfig(2, "PAM"))


@pytest.mark.parametrize("transmitted,decided,expected", [
    ([[-1.0], [1.0]], [[-1.0], [1.0]], 0.0),
    ([[-1.0], [1.0]], [[1.0], [-1.0]], 1.0),
    ([[1.0, 0.0], [0.0, 1.0], [1.0, 0.0], [0.0, 1.0]],
     [[1.0, 0.0], [1.0, 0.0], [1.0, 0.0], [0.0, 1.0]], 0.25),
])
def test_known_ser(transmitted: list[list[float]], decided: list[list[float]], expected: float) -> None:
    """Cambiar varias coordenadas de una fila cuenta como un solo error."""
    assert available(estimate_symbol_error_rate, np.array(transmitted), np.array(decided)) == expected


@pytest.mark.parametrize("transmitted,decided", [
    (np.empty((0, 1)), np.empty((0, 1))),
    (np.array([[1.0]]), np.array([[1.0], [-1.0]])),
    (np.array([[1.0, 0.0]]), np.array([[1.0]])),
    (np.array([[1.0]]), np.array([[float("inf")]])),
])
def test_invalid_ser_vectors(transmitted: np.ndarray, decided: np.ndarray) -> None:
    """La comparación no debe truncar vectores ni aceptar vacíos."""
    with pytest.raises(ValueError):
        available(estimate_symbol_error_rate, transmitted, decided)


@pytest.mark.parametrize("transmitted,received,expected", [
    ("0101", "0101", 0.0), ("0101", "1010", 1.0), ("0101", "0111", 0.25),
])
def test_known_ber(transmitted: str, received: str, expected: float) -> None:
    """Los resultados se especifican manualmente y corresponden a bits sin relleno."""
    assert available(estimate_bit_error_rate, transmitted, received) == expected


@pytest.mark.parametrize("transmitted,received", [("", ""), ("01", "0"), ("02", "01"), ("01", "0a")])
def test_invalid_ber_vectors(transmitted: str, received: str) -> None:
    """La comparación debe exigir dos cadenas binarias no vacías de igual largo."""
    with pytest.raises(ValueError):
        available(estimate_bit_error_rate, transmitted, received)


@pytest.mark.parametrize("tipo,expected", [("PAM", 0.078649603525), ("FSK", 0.158655253931)])
def test_binary_awgn_reference(tipo: str, expected: float) -> None:
    """Referencia binaria coherente a Eb/N0=0 dB, sin codificación de canal."""
    result = available(theoretical_error_rates, ModulationConfig(2, tipo), 0.0)
    assert result.symbol_error_rate == pytest.approx(expected)
    assert result.bit_error_rate == pytest.approx(expected)


@pytest.mark.parametrize("eb_n0_db", [float("nan"), float("inf"), float("-inf")])
def test_invalid_awgn_reference(eb_n0_db: float) -> None:
    """La relación de energía teórica debe ser finita."""
    with pytest.raises(ValueError):
        available(theoretical_error_rates, ModulationConfig(2, "PAM"), eb_n0_db)


def test_histogram_includes_unobserved_symbols() -> None:
    """Conserva filas en cero y sigue el orden de etiquetas, no el de aparición."""
    constellation = Constellation(np.array([[-3.0], [-1.0], [1.0], [3.0]]), ["00", "01", "11", "10"])
    data = ModulatedData(np.array([[1.0], [-3.0], [-3.0], [-3.0]]), 1)
    result = available(symbol_statistics, data, constellation)
    assert result.labels == ["00", "01", "11", "10"]
    np.testing.assert_array_equal(result.counts, [3, 0, 1, 0])
    np.testing.assert_allclose(result.probabilities, [0.75, 0.0, 0.25, 0.0])


@pytest.mark.parametrize("symbols", [np.empty((0, 1)), np.array([[2.0]]), np.array([[1.0, 0.0]])])
def test_invalid_histogram_sample(symbols: np.ndarray) -> None:
    """La muestra debe ser no vacía y pertenecer a la constelación dada."""
    constellation = Constellation(np.array([[-1.0], [1.0]]), ["0", "1"])
    with pytest.raises(ValueError):
        available(symbol_statistics, ModulatedData(symbols), constellation)
