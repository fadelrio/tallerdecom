"""Casos funcionales futuros del receptor, sin implementar decisiones aquí."""

from collections.abc import Callable

import numpy as np
import pytest

from common.constellations import build_constellation
from common.data_types import EncodedSource, ModulatedData
from config import ModulationConfig
from receiver.demodulation import demodulation, demodulation_FSK, demodulation_PAM
from tests._pending import available
from transmitter.modulation import modulation


@pytest.mark.parametrize("tipo,function,symbols", [
    ("PAM", demodulation_PAM, [[-0.9], [0.8], [-1.2]]),
    ("FSK", demodulation_FSK, [[0.9, 0.1], [0.1, 0.8], [1.2, -0.1]]),
])
def test_known_decisions(tipo: str, function: Callable, symbols: list[list[float]]) -> None:
    """Pequeñas perturbaciones no cambian las decisiones binarias conocidas."""
    result = available(function, ModulatedData(np.array(symbols)), ModulationConfig(2, tipo))
    assert result.bits == "010"
    expected = [[-1.0], [1.0], [-1.0]] if tipo == "PAM" else [[1.0, 0.0], [0.0, 1.0], [1.0, 0.0]]
    np.testing.assert_allclose(result.symbols, expected)


@pytest.mark.parametrize("tipo,coordinates,expected", [
    ("PAM", [[0.0]], [[-1.0]]),
    ("FSK", [[0.5, 0.5]], [[1.0, 0.0]]),
])
def test_decision_tie(tipo: str, coordinates: list[list[float]], expected: list[list[float]]) -> None:
    """Un empate se resuelve por la primera fila de la constelación."""
    result = available(demodulation, ModulatedData(np.array(coordinates)), ModulationConfig(2, tipo))
    assert result.bits == "0"
    np.testing.assert_allclose(result.symbols, expected)


@pytest.mark.parametrize("tipo", ["PAM", "FSK"])
@pytest.mark.parametrize("M", [2, 4, 8, 16])
@pytest.mark.parametrize("bits", ["", "0", "10101", "00011110110010"])
def test_round_trip(tipo: str, M: int, bits: str) -> None:
    """La ida y vuelta Gray recuperará los bits y conservará todos los símbolos."""
    config = ModulationConfig(M, tipo)
    transmitted = available(modulation, EncodedSource(bits), config)
    result = available(demodulation, transmitted, config)
    assert result.bits == bits
    np.testing.assert_allclose(result.symbols, transmitted.symbols)


@pytest.mark.parametrize("tipo", ["PAM", "FSK"])
@pytest.mark.parametrize("labeling,expected", [("gray", "00011110"), ("binary", "00011011")])
def test_demodulator_uses_labels(tipo: str, labeling: str, expected: str) -> None:
    """Las etiquetas se recuperan en el orden de la constelación compartida."""
    config = ModulationConfig(4, tipo, labeling=labeling)
    constellation = available(build_constellation, config)
    result = available(demodulation, ModulatedData(constellation.symbols), config)
    assert result.bits == expected


@pytest.mark.parametrize("tipo", ["PAM", "FSK"])
def test_channel_coded_constellation_decisions(tipo: str) -> None:
    """El receptor usará la misma escala de canal que la constelación transmitida."""
    config = ModulationConfig(2, tipo, code_rate=0.5)
    constellation = available(build_constellation, config)
    result = available(demodulation, ModulatedData(constellation.symbols), config)
    assert result.bits == "01"
    np.testing.assert_allclose(result.symbols, constellation.symbols)


@pytest.mark.parametrize("data", [
    ModulatedData(np.array([[1.0, 0.0]])),
    ModulatedData(np.array([[float("nan")]])),
    ModulatedData(np.array([[-1.0]]), -1),
    ModulatedData(np.array([[-1.0]]), 1),
    ModulatedData(np.empty((0, 1)), 1),
])
def test_incompatible_received_data(data: ModulatedData) -> None:
    """Se rechazarán dimensión, valores o metadatos de relleno incompatibles."""
    with pytest.raises(ValueError):
        available(demodulation, data, ModulationConfig(2, "PAM"))
