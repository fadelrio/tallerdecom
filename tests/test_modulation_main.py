"""Orquestación activa con bloques sustituidos y aceptación futura del flujo real."""

from pathlib import Path
from unittest.mock import Mock

import numpy as np
import pytest

import main as application
from common.data_types import (
    Constellation, DemodulatedData, EnergyStatistics, ErrorRates,
    ModulatedData, SymbolStatistics,
)
from config import ModulationConfig, SimulationConfig
from main import run_modulation_simulation
from tests._pending import available


@pytest.fixture
def pipeline(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> dict:
    """Sustituye los cálculos pendientes por datos manuales para probar conexiones."""
    source = tmp_path / "entrada.txt"
    output = tmp_path / "recibido.txt"
    source.write_bytes("ñññ".encode("utf-8"))
    constellation = Constellation(
        np.array([[-1.897366596101], [-0.632455532034], [0.632455532034], [1.897366596101]]),
        ["00", "01", "11", "10"],
    )
    transmitted = ModulatedData(np.array([[-1.897366596101], [-1.897366596101]]), 1)
    decided = DemodulatedData(transmitted.symbols.copy(), "000")
    statistics = SymbolStatistics(constellation.labels, np.array([2, 0, 0, 0]), np.array([1.0, 0.0, 0.0, 0.0]))
    values = {
        "build_constellation": constellation,
        "modulation": transmitted,
        "demodulation": decided,
        "estimate_energies": EnergyStatistics(3.6, 1.8, 1.8),
        "theoretical_energies": EnergyStatistics(2.0, 1.0, 1.0),
        "estimate_symbol_error_rate": 0.0,
        "estimate_bit_error_rate": 0.0,
        "theoretical_error_rates": ErrorRates(0.125, 0.0625),
        "symbol_statistics": statistics,
        "plot_constellation": None,
        "plot_symbol_histogram": None,
    }
    mocks = {}
    for name, value in values.items():
        mocks[name] = Mock(return_value=value)
        monkeypatch.setattr(application, name, mocks[name])
    return {"paths": SimulationConfig(source, output), "mocks": mocks, "values": values}


def test_orchestration_uses_received_bits_and_all_blocks(pipeline: dict, capsys: pytest.CaptureFixture[str]) -> None:
    """Conecta los bloques y no elimina por segunda vez el bit de relleno."""
    paths = pipeline["paths"]
    mocks = pipeline["mocks"]
    values = pipeline["values"]
    config = ModulationConfig(4, "PAM")
    assert run_modulation_simulation(paths, config, eb_n0_db=7.5) is None
    assert paths.output_file.read_bytes() == paths.input_file.read_bytes()
    assert mocks["modulation"].call_args.args[0].bits == "000"
    mocks["build_constellation"].assert_called_once_with(config)
    mocks["demodulation"].assert_called_once_with(values["modulation"], config)
    mocks["estimate_energies"].assert_called_once_with(values["modulation"].symbols, config)
    mocks["theoretical_energies"].assert_called_once_with(config)
    mocks["estimate_symbol_error_rate"].assert_called_once_with(values["modulation"].symbols, values["demodulation"].symbols)
    mocks["estimate_bit_error_rate"].assert_called_once_with("000", "000")
    mocks["theoretical_error_rates"].assert_called_once_with(config, 7.5)
    mocks["symbol_statistics"].assert_called_once_with(values["modulation"], values["build_constellation"])
    mocks["plot_constellation"].assert_called_once_with(values["build_constellation"], paths.output_file.with_name("recibido.txt.constellation.png"))
    mocks["plot_symbol_histogram"].assert_called_once_with(values["symbol_statistics"], paths.output_file.with_name("recibido.txt.histogram.png"))
    output = capsys.readouterr().out
    assert "sin ruido" in output and "Eb/N0 = 7.5 dB" in output
    assert "Bits de relleno: 1" in output and "Texto idéntico: True" in output
    assert "| SER | 0.125 | 0 |" in output


def test_orchestration_default_reference(pipeline: dict) -> None:
    """Los dos argumentos originales siguen siendo válidos; la referencia es 0 dB."""
    config = ModulationConfig(4, "PAM")
    run_modulation_simulation(pipeline["paths"], config)
    pipeline["mocks"]["theoretical_error_rates"].assert_called_once_with(config, 0.0)


@pytest.mark.parametrize("name", [
    "build_constellation", "modulation", "demodulation", "estimate_energies",
    "theoretical_energies", "estimate_symbol_error_rate", "estimate_bit_error_rate",
    "theoretical_error_rates", "symbol_statistics", "plot_constellation", "plot_symbol_histogram",
])
def test_orchestration_propagates_pending_blocks(name: str, pipeline: dict) -> None:
    """Un bloque pendiente no se oculta ni sobrescribe el archivo recibido."""
    paths = pipeline["paths"]
    paths.output_file.write_text("conservar", encoding="utf-8")
    pipeline["mocks"][name].side_effect = NotImplementedError(name)
    with pytest.raises(NotImplementedError, match=name):
        run_modulation_simulation(paths, ModulationConfig(4, "PAM"))
    assert paths.output_file.read_text(encoding="utf-8") == "conservar"


@pytest.mark.parametrize("changes", [{"labeling": "binary"}, {"code_rate": 0.5}])
def test_unimplemented_modulator_options_are_explicit(changes: dict, pipeline: dict) -> None:
    """El selector existente no debe ignorar opciones solicitadas en silencio."""
    with pytest.raises(NotImplementedError, match="selector"):
        run_modulation_simulation(pipeline["paths"], ModulationConfig(4, "PAM", **changes))
    pipeline["mocks"]["modulation"].assert_not_called()


@pytest.mark.parametrize("value,error", [(float("nan"), ValueError), (float("inf"), ValueError), ("0", TypeError), (True, TypeError)])
def test_invalid_reference(value: object, error: type[Exception], pipeline: dict) -> None:
    """La referencia inválida se rechaza antes de transmitir."""
    with pytest.raises(error):
        run_modulation_simulation(pipeline["paths"], ModulationConfig(4, "PAM"), eb_n0_db=value)
    pipeline["mocks"]["modulation"].assert_not_called()


@pytest.mark.parametrize("case", ["empty", "missing", "invalid_utf8", "same_path", "plot_is_input"])
def test_input_errors_do_not_start_transmission(case: str, pipeline: dict, capsys: pytest.CaptureFixture[str]) -> None:
    """Errores de entrada no deben modificar la salida ni comenzar el flujo."""
    paths = pipeline["paths"]
    paths.output_file.write_text("conservar", encoding="utf-8")
    if case == "empty":
        paths.input_file.write_text("", encoding="utf-8")
    elif case == "missing":
        paths = SimulationConfig(paths.input_file.with_name("ausente.txt"), paths.output_file)
    elif case == "invalid_utf8":
        paths.input_file.write_bytes(b"\xff")
    elif case == "same_path":
        paths = SimulationConfig(paths.output_file, paths.output_file)
    else:
        paths = SimulationConfig(paths.output_file.with_name("recibido.txt.constellation.png"), paths.output_file)
        paths.input_file.write_text("fuente", encoding="utf-8")
    run_modulation_simulation(paths, ModulationConfig(4, "PAM"))
    assert "[ERROR]" in capsys.readouterr().out
    assert paths.output_file.read_text(encoding="utf-8") == "conservar"
    pipeline["mocks"]["modulation"].assert_not_called()


def test_output_error_is_reported(pipeline: dict, capsys: pytest.CaptureFixture[str]) -> None:
    """No se anuncia una simulación completada si falla la generación de salidas."""
    pipeline["mocks"]["plot_constellation"].side_effect = OSError("sin permiso")
    run_modulation_simulation(pipeline["paths"], ModulationConfig(4, "PAM"))
    assert "[ERROR]" in capsys.readouterr().out
    assert not pipeline["paths"].output_file.exists()


@pytest.mark.parametrize("tipo", ["PAM", "FSK"])
def test_modulation_file_round_trip(tipo: str, tmp_path: Path) -> None:
    """La futura conexión sin ruido debe recuperar el archivo UTF-8 completo."""
    source = tmp_path / "entrada.txt"
    output = tmp_path / "recibido.txt"
    source.write_bytes("\ufeffInformación\r\nñá\n".encode("utf-8"))
    result = available(run_modulation_simulation, SimulationConfig(source, output), ModulationConfig(4, tipo))
    assert result is None
    assert output.read_bytes() == source.read_bytes()
