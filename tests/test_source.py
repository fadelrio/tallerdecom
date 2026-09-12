"""Pruebas de interfaces y ejecución; no verifican algoritmos pendientes."""

import importlib
import inspect
import subprocess
import sys
from dataclasses import is_dataclass
from pathlib import Path
from typing import get_type_hints

import pytest

from common.data_types import (
    CodeStatistics,
    CodingReport,
    EncodedSource,
    FileComparison,
    HuffmanResult,
    SourceReport,
    SourceStatistics,
)
from config import SimulationConfig, load_config


MODULES = (
    "main", "config", "common", "common.data_types", "common.file_utils",
    "common.report_utils", "transmitter", "transmitter.source_analysis",
    "transmitter.huffman", "transmitter.source_encoder", "receiver",
    "receiver.source_decoder",
)

CONTRACTS = (
    ("transmitter.source_analysis", "analyze_source",
     {"data": bytes, "return": SourceStatistics}),
    ("transmitter.huffman", "build_huffman_code",
     {"probabilities": dict[int, float], "return": HuffmanResult}),
    ("transmitter.huffman", "calculate_efficiency",
     {"entropy": float, "average_length": float, "return": float}),
    ("transmitter.source_encoder", "encode_source",
     {"data": bytes, "codebook": dict[int, str], "return": EncodedSource}),
    ("receiver.source_decoder", "decode_source",
     {"encoded": EncodedSource, "codebook": dict[int, str], "return": bytes}),
    ("common.file_utils", "read_file",
     {"path": Path, "return": bytes}),
    ("common.file_utils", "write_file",
     {"path": Path, "data": bytes, "return": type(None)}),
    ("common.file_utils", "compare_data",
     {"original": bytes, "received": bytes, "return": FileComparison}),
    ("common.report_utils", "build_source_table",
     {"statistics": SourceStatistics, "huffman": HuffmanResult,
      "return": list[SourceReport]}),
    ("common.report_utils", "build_coding_report",
     {"statistics": SourceStatistics, "huffman": HuffmanResult,
      "encoded": EncodedSource, "return": CodingReport}),
    ("config", "load_config", {"return": SimulationConfig}),
    ("main", "main", {"return": type(None)}),
)


@pytest.mark.parametrize("module_name", MODULES)
def test_modules_import(module_name: str) -> None:
    """Verifica que cada módulo pueda importarse.

    Args:
        module_name: Nombre del módulo bajo prueba.
    """
    assert importlib.import_module(module_name) is not None


def test_data_structures() -> None:
    """Verifica la instanciación y documentación con datos manuales."""
    statistics = SourceStatistics({0: 1, 255: 1}, {0: 0.5, 255: 0.5}, 2, 1.0)
    code = CodeStatistics(1, 1.0, 0.0, True)
    huffman = HuffmanResult({0: "0", 255: "1"}, code)
    encoded = EncodedSource("01")
    comparison = FileComparison(True, 2, 2)
    row = SourceReport(255, 1, 0.5, "1")
    report = CodingReport(1.0, 1, 1.0, 0.0, 1.0, 8, 2, 16)
    config = SimulationConfig(Path("entrada.bin"), Path("recibido.bin"))
    instances = (statistics, code, huffman, encoded, comparison, row,
                 report, config)
    for instance in instances:
        assert is_dataclass(instance)
        assert "Attributes:" in inspect.getdoc(type(instance))
    assert statistics.counts == {0: 1, 255: 1}
    assert huffman.statistics is code
    assert encoded.bits == "01"
    assert row.symbol == 255
    assert report.fixed_code_length == 8
    assert isinstance(config.input_file, Path)


@pytest.mark.parametrize("module_name, name, expected", CONTRACTS)
def test_function_contracts(
    module_name: str,
    name: str,
    expected: dict[str, object],
) -> None:
    """Verifica nombres, anotaciones y documentación de las interfaces.

    Args:
        module_name: Módulo que declara la función.
        name: Nombre de la función pública.
        expected: Anotaciones esperadas, incluido el retorno.
    """
    function = getattr(importlib.import_module(module_name), name)
    assert get_type_hints(function) == expected
    assert list(inspect.signature(function).parameters) == [
        key for key in expected if key != "return"
    ]
    assert inspect.getdoc(function)


@pytest.mark.parametrize("module_name, name, expected", CONTRACTS[:-2])
def test_placeholders_are_explicit(
    module_name: str,
    name: str,
    expected: dict[str, object],
) -> None:
    """Comprueba el contrato temporal de funcionalidades pendientes.

    Args:
        module_name: Módulo del placeholder.
        name: Nombre de la función pendiente.
        expected: Interfaz usada para suministrar argumentos de ejemplo.

    Notes:
        Reemplazar estas pruebas por pruebas funcionales al implementar
        cada interfaz. No se espera ningún resultado algorítmico real.
    """
    samples = {
        "data": b"\x00\xff", "probabilities": {0: 0.5, 255: 0.5},
        "entropy": 1.0, "average_length": 1.0,
        "codebook": {0: "0", 255: "1"}, "encoded": EncodedSource("01"),
        "path": Path("no_crear.bin"), "original": b"\x00\xff",
        "received": b"\x00\xff",
        "statistics": SourceStatistics({}, {}, 0, 0.0),
        "huffman": HuffmanResult({}, CodeStatistics(0, 0.0, 0.0, False)),
    }
    function = getattr(importlib.import_module(module_name), name)
    arguments = {key: samples[key] for key in expected if key != "return"}
    with pytest.raises(NotImplementedError):
        function(**arguments)


def test_config_paths() -> None:
    """Verifica que la configuración devuelva rutas Path independientes."""
    config = load_config()
    assert isinstance(config.input_file, Path)
    assert isinstance(config.output_file, Path)
    assert config.input_file != config.output_file


def test_main_runs_without_input_file(tmp_path: Path) -> None:
    """Ejecuta el programa sin archivos y verifica estados y ausencia de E/S.

    Args:
        tmp_path: Directorio temporal provisto por pytest.
    """
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, str(root / "main.py")],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert result.stderr == ""
    for section in ("[CONFIG]", "[TRANSMISOR]", "[CANAL]", "[RECEPTOR]",
                    "[RESULTADO]"):
        assert section in result.stdout
    assert "[PENDIENTE]" in result.stdout
    assert "[NO IMPLEMENTADO]" in result.stdout
    assert "Demodulación" in result.stdout
    assert "Comparación" in result.stdout
    assert list(tmp_path.iterdir()) == []
