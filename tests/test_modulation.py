"""Casos de PAM existente y comportamiento futuro de constelaciones y FSK."""

import numpy as np
import pytest

from common.constellations import build_constellation
from common.data_types import EncodedSource
from config import ModulationConfig, validate_modulation_config
from tests._pending import available
from transmitter.modulation import modulation, modulation_FSK, modulation_PAM


# Entradas y resultados manuales: no reconstruir el algoritmo bajo prueba.
WORDS = {
    2: "01",
    4: "00011110",
    8: "000001011010110111101100",
    16: "0000000100110010011001110101010011001101111111101010101110011000",
}
LABELS = {
    2: ["0", "1"],
    4: ["00", "01", "11", "10"],
    8: ["000", "001", "011", "010", "110", "111", "101", "100"],
    16: ["0000", "0001", "0011", "0010", "0110", "0111", "0101", "0100",
         "1100", "1101", "1111", "1110", "1010", "1011", "1001", "1000"],
}


@pytest.mark.parametrize("M", [2, 4, 8, 16])
def test_existing_pam_shape_and_order(M: int) -> None:
    """PAM existente representa una vez cada nivel en orden creciente."""
    result = modulation_PAM(EncodedSource(WORDS[M]), M)
    assert result.symbols.shape == (M, 1)
    assert result.padding_bits == 0
    assert np.all(np.diff(result.symbols[:, 0]) > 0)


def test_existing_pam_known_mapping() -> None:
    """Fija una referencia manual de 4-PAM Gray para proteger el código actual."""
    result = modulation(EncodedSource("00011110"), ModulationConfig(4, "PAM"))
    np.testing.assert_allclose(result.symbols[:, 0],
                               [-1.897366596101, -0.632455532034, 0.632455532034, 1.897366596101])


@pytest.mark.parametrize("bits,padding,count", [("", 0, 0), ("101", 1, 2), ("1010", 0, 2)])
def test_existing_pam_padding(bits: str, padding: int, count: int) -> None:
    """Conserva el contrato de entrada vacía y relleno de PAM."""
    result = modulation_PAM(EncodedSource(bits), 4)
    assert result.padding_bits == padding
    assert result.symbols.shape == (count, 1)


@pytest.mark.parametrize("tipo", ["PAM", "FSK"])
@pytest.mark.parametrize("M", [2, 4, 8, 16])
@pytest.mark.parametrize("labeling", ["gray", "binary"])
def test_valid_config(tipo: str, M: int, labeling: str) -> None:
    """El validador admite todos los órdenes y etiquetas acordados."""
    assert validate_modulation_config(ModulationConfig(M, tipo, labeling=labeling)) is None


@pytest.mark.parametrize("changes", [
    {"M": 1}, {"M": 0}, {"M": 3}, {"M": 32}, {"tipo": "PSK"},
    {"labeling": "otro"}, {"Eb": 0.0}, {"Eb": -1.0}, {"Eb": float("nan")},
    {"Eb": float("inf")}, {"code_rate": 0.0}, {"code_rate": 1.1},
    {"code_rate": float("nan")}, {"code_rate": float("inf")},
])
def test_invalid_config(changes: dict[str, object]) -> None:
    """Los parámetros inválidos deben fallar sin omisiones."""
    fields = {"M": 4, "tipo": "PAM", **changes}
    with pytest.raises(ValueError):
        validate_modulation_config(ModulationConfig(**fields))


@pytest.mark.parametrize("M", [2.0, "4", True])
def test_invalid_order_type(M: object) -> None:
    """El orden debe ser entero y no booleano."""
    with pytest.raises(TypeError):
        validate_modulation_config(ModulationConfig(M, "PAM"))


@pytest.mark.parametrize("tipo", ["PAM", "FSK"])
@pytest.mark.parametrize("M", [2, 4, 8, 16])
def test_gray_constellation(tipo: str, M: int) -> None:
    """La futura tabla tendrá etiquetas Gray y la dimensión del esquema."""
    result = available(build_constellation, ModulationConfig(M, tipo))
    assert result.symbols.shape == (M, 1 if tipo == "PAM" else M)
    assert result.labels == LABELS[M]
    if tipo == "PAM":
        assert np.all(np.diff(result.symbols[:, 0]) > 0)


@pytest.mark.parametrize("tipo", ["PAM", "FSK"])
def test_binary_constellation(tipo: str) -> None:
    """Binario y Gray usan las mismas coordenadas y distintas etiquetas."""
    binary = available(build_constellation, ModulationConfig(4, tipo, labeling="binary"))
    gray = available(build_constellation, ModulationConfig(4, tipo))
    assert binary.labels == ["00", "01", "10", "11"]
    np.testing.assert_allclose(binary.symbols, gray.symbols)


@pytest.mark.parametrize("tipo,expected", [
    ("PAM", [[-1.0], [1.0]]),
    ("FSK", [[1.0, 0.0], [0.0, 1.0]]),
])
def test_known_constellation(tipo: str, expected: list[list[float]]) -> None:
    """Referencia manual de energía unitaria para los esquemas binarios."""
    result = available(build_constellation, ModulationConfig(2, tipo))
    np.testing.assert_allclose(result.symbols, expected)


@pytest.mark.parametrize("tipo,expected", [
    ("PAM", [[-0.707106781187], [0.707106781187]]),
    ("FSK", [[0.707106781187, 0.0], [0.0, 0.707106781187]]),
])
def test_constellation_channel_rate(tipo: str, expected: list[list[float]]) -> None:
    """La futura normalización tendrá en cuenta la tasa de canal."""
    result = available(build_constellation, ModulationConfig(2, tipo, code_rate=0.5))
    np.testing.assert_allclose(result.symbols, expected)


@pytest.mark.parametrize("M", [2, 4, 8, 16])
def test_fsk_order_and_shape(M: int) -> None:
    """El caso básico FSK usará Gray por orden de ejes, como la tabla común."""
    result = available(modulation_FSK, EncodedSource(WORDS[M]), M)
    assert result.symbols.shape == (M, M)
    assert result.padding_bits == 0
    np.testing.assert_array_equal(np.argmax(result.symbols, axis=1), np.arange(M))
    assert np.all(np.count_nonzero(result.symbols, axis=1) == 1)
    assert np.all(np.diag(result.symbols) > 0)


def test_fsk_known_mapping() -> None:
    """La referencia binaria FSK tiene coordenadas unitarias en ejes distintos."""
    result = available(modulation_FSK, EncodedSource("01"), 2)
    np.testing.assert_allclose(result.symbols, [[1.0, 0.0], [0.0, 1.0]])


@pytest.mark.parametrize("bits,padding,count", [("", 0, 0), ("101", 1, 2), ("1010", 0, 2)])
def test_fsk_padding(bits: str, padding: int, count: int) -> None:
    """FSK conservará los mismos metadatos de relleno que PAM."""
    result = available(modulation_FSK, EncodedSource(bits), 4)
    assert result.padding_bits == padding
    assert result.symbols.shape == (count, 4)


@pytest.mark.parametrize("bits", ["012", "a", "0 1"])
def test_fsk_invalid_bits(bits: str) -> None:
    """No se deben mapear caracteres ajenos al alfabeto binario."""
    with pytest.raises(ValueError):
        available(modulation_FSK, EncodedSource(bits), 4)


@pytest.mark.parametrize("M,Eb", [(1, 1.0), (3, 1.0), (32, 1.0), (4, 0.0), (4, -1.0)])
def test_fsk_invalid_parameters(M: int, Eb: float) -> None:
    """El auxiliar FSK también deberá rechazar parámetros fuera del contrato."""
    with pytest.raises(ValueError):
        available(modulation_FSK, EncodedSource("01"), M, Eb)
