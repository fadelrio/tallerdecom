"""Contratos activos del apartado, incluso cuando los cálculos están pendientes."""

import importlib
import inspect
import runpy
from dataclasses import is_dataclass
from pathlib import Path
from typing import get_type_hints

import numpy as np
import pytest

from common.data_types import (
    Constellation, DemodulatedData, EncodedSource, EnergyStatistics,
    ErrorRates, ModulatedData, SymbolStatistics,
)
from config import ModulationConfig, SimulationConfig, load_modulation_config
from tests._pending import available


MODULES = (
    "transmitter.modulation", "receiver.demodulation", "common.constellations",
    "common.modulation_metrics", "common.modulation_plots", "common.modulation_report",
)

CONTRACTS = (
    ("config", "validate_modulation_config", {"config": ModulationConfig, "return": type(None)}),
    ("common.constellations", "build_constellation", {"config": ModulationConfig, "return": Constellation}),
    ("transmitter.modulation", "modulation", {"encoded": EncodedSource, "Modulacion_config": ModulationConfig, "return": ModulatedData}),
    ("transmitter.modulation", "modulation_PAM", {"encoded": EncodedSource, "M": int, "Eb": float, "return": ModulatedData}),
    ("transmitter.modulation", "modulation_FSK", {"encoded": EncodedSource, "M": int, "Eb": float, "return": ModulatedData}),
    *[("receiver.demodulation", name, {"modulated": ModulatedData, "config": ModulationConfig, "return": DemodulatedData})
      for name in ("demodulation", "demodulation_PAM", "demodulation_FSK")],
    ("common.modulation_metrics", "estimate_energies", {"symbols": np.ndarray, "config": ModulationConfig, "return": EnergyStatistics}),
    ("common.modulation_metrics", "theoretical_energies", {"config": ModulationConfig, "return": EnergyStatistics}),
    ("common.modulation_metrics", "estimate_symbol_error_rate", {"transmitted": np.ndarray, "decided": np.ndarray, "return": float}),
    ("common.modulation_metrics", "estimate_bit_error_rate", {"transmitted": str, "received": str, "return": float}),
    ("common.modulation_metrics", "theoretical_error_rates", {"config": ModulationConfig, "eb_n0_db": float, "return": ErrorRates}),
    ("common.modulation_metrics", "symbol_statistics", {"modulated": ModulatedData, "constellation": Constellation, "return": SymbolStatistics}),
    ("common.modulation_plots", "plot_constellation", {"constellation": Constellation, "output_file": Path, "return": type(None)}),
    ("common.modulation_plots", "plot_symbol_histogram", {"statistics": SymbolStatistics, "output_file": Path, "return": type(None)}),
    ("common.modulation_report", "format_modulation_report", {"config": ModulationConfig, "theoretical_energies": EnergyStatistics, "estimated_energies": EnergyStatistics, "theoretical_errors": ErrorRates, "estimated_errors": ErrorRates, "statistics": SymbolStatistics, "return": str}),
    ("main", "run_modulation_simulation", {"config": SimulationConfig, "modulation_config": ModulationConfig, "eb_n0_db": float, "return": type(None)}),
)


@pytest.mark.parametrize("module_name", MODULES)
def test_modules_import(module_name: str) -> None:
    """Los módulos pendientes deben poder importarse sin ejecutar simulaciones."""
    assert importlib.import_module(module_name) is not None


@pytest.mark.parametrize("module_name,name,expected", CONTRACTS)
def test_function_contracts(module_name: str, name: str, expected: dict[str, object]) -> None:
    """Comprueba firmas, anotaciones y documentación de interfaces públicas."""
    function = getattr(importlib.import_module(module_name), name)
    assert get_type_hints(function) == expected
    assert list(inspect.signature(function).parameters) == [
        key for key in expected if key != "return"
    ]
    doc = inspect.getdoc(function)
    assert doc and "Args:" in doc and "Returns:" in doc


def test_modulation_data_structures() -> None:
    """Las dataclasses conservan datos manuales sin calcular ni decidir."""
    symbols = np.array([[-1.0], [1.0]])
    labels = ["0", "1"]
    counts = np.array([3, 1])
    probabilities = np.array([0.75, 0.25])
    constellation = Constellation(symbols, labels)
    decided = DemodulatedData(symbols, "01")
    energies = EnergyStatistics(2.0, 1.0, 2.0)
    errors = ErrorRates(0.25, 0.125)
    statistics = SymbolStatistics(labels, counts, probabilities)
    modulated = ModulatedData(symbols, 1)
    for instance in (constellation, decided, energies, errors, statistics, modulated):
        assert is_dataclass(instance)
        assert "Attributes:" in inspect.getdoc(type(instance))
    assert constellation.symbols is symbols and constellation.labels is labels
    assert decided.symbols is symbols and decided.bits == "01"
    assert energies.symbol_energy == 2.0
    assert energies.channel_bit_energy == 1.0 and energies.bit_energy == 2.0
    assert errors.symbol_error_rate == 0.25 and errors.bit_error_rate == 0.125
    assert statistics.counts is counts and statistics.probabilities is probabilities
    assert modulated.padding_bits == 1


def test_modulation_config_is_backward_compatible() -> None:
    """Los argumentos anteriores y los nuevos campos pueden coexistir."""
    previous = load_modulation_config(4, "PAM", 1.0)
    assert previous == ModulationConfig(4, "PAM", 1.0)
    assert previous.labeling == "gray" and previous.code_rate == 1.0
    configured = ModulationConfig(8, "FSK", labeling="binary", code_rate=0.5)
    assert configured.labeling == "binary" and configured.code_rate == 0.5


def test_pending_helper_returns_results() -> None:
    """Una función implementada llega a las aserciones del caso funcional."""
    def implemented(value: str) -> str:
        return value

    assert available(implemented, "resultado") == "resultado"


def test_pending_helper_only_skips_not_implemented() -> None:
    """Los errores reales no deben convertirse en pruebas omitidas."""
    def pending() -> None:
        raise NotImplementedError("pendiente de ejemplo")

    def invalid() -> None:
        raise ValueError("dato inválido")

    with pytest.raises(pytest.skip.Exception, match="pendiente de ejemplo"):
        available(pending)
    with pytest.raises(ValueError, match="dato inválido"):
        available(invalid)


def test_pam_experiment_import_has_no_io(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """Importar o recargar el experimento no debe ejecutar ninguno de los flujos."""
    import common.file_utils as files
    import main

    def unexpected(*args: object, **kwargs: object) -> None:
        pytest.fail("Importar el experimento no debe hacer E/S ni simular")

    with monkeypatch.context() as guarded:
        guarded.setattr(files, "read_file", unexpected)
        guarded.setattr(files, "write_file", unexpected)
        guarded.setattr(main, "run_simulation", unexpected)
        module = importlib.import_module("experiments.experimento_PAM")
        importlib.reload(module)
        assert callable(module.run_pam_experiment)
        assert capsys.readouterr().out == ""
    # Restaurar también los imports enlazados dentro del módulo del experimento.
    importlib.reload(module)


def test_pam_experiment_entrypoint(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """El bloque principal ejecuta el experimento local sin escribir archivos."""
    import common.file_utils as files
    import main

    reads = []

    def read_fixture(path: Path) -> str:
        reads.append(path)
        return "AAAA"

    def unexpected(*args: object, **kwargs: object) -> None:
        pytest.fail("El experimento no debe escribir ni llamar al flujo anterior")

    monkeypatch.setattr(files, "read_file", read_fixture)
    monkeypatch.setattr(files, "write_file", unexpected)
    monkeypatch.setattr(main, "run_simulation", unexpected)
    path = Path(__file__).resolve().parents[1] / "experiments" / "experimento_PAM.py"
    runpy.run_path(str(path), run_name="__main__")
    output = capsys.readouterr().out
    assert len(reads) == 1
    assert "# EXPERIMENTO PAM" in output
    assert "Dimensión de los datos modulados: (1, 1)" in output
