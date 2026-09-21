"""Pruebas de interfaces y ejecución; no verifican algoritmos pendientes."""

import importlib
import inspect
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
     {"data": str, "return": SourceStatistics}),
    ("transmitter.huffman", "build_huffman_code",
     {"probabilities": dict[str, float], "return": HuffmanResult}),
    ("transmitter.huffman", "calculate_efficiency",
     {"entropy": float, "average_length": float, "return": float}),
    ("transmitter.source_encoder", "encode_source",
     {"data": str, "codebook": dict[str, str], "return": EncodedSource}),
    ("receiver.source_decoder", "decode_source",
     {"encoded": EncodedSource, "codebook": dict[str, str], "return": str}),
    ("common.file_utils", "read_file",
     {"path": Path, "return": str}),
    ("common.file_utils", "write_file",
     {"path": Path, "data": str, "return": type(None)}),
    ("common.file_utils", "compare_data",
     {"original": str, "received": str, "return": FileComparison}),
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
    statistics = SourceStatistics({'\x00': 1, 'ÿ': 1}, {'\x00': 0.5, 'ÿ': 0.5}, 2, 1.0)
    code = CodeStatistics(1, 1.0, 0.0, True)
    huffman = HuffmanResult({'\x00': "0", 'ÿ': "1"}, code)
    encoded = EncodedSource("01")
    comparison = FileComparison(True, 2, 2)
    row = SourceReport("ÿ", 1, 0.5, "1")
    report = CodingReport(1.0, 1, 1.0, 0.0, 1.0, 8, 2, 16)
    config = SimulationConfig(Path("entrada.txt"), Path("recibido.txt"))
    instances = (statistics, code, huffman, encoded, comparison, row,
                 report, config)
    for instance in instances:
        assert is_dataclass(instance)
        assert "Attributes:" in inspect.getdoc(type(instance))
    assert statistics.counts == {'\x00': 1, 'ÿ': 1}
    assert huffman.statistics is code
    assert encoded.bits == "01"
    assert row.symbol == "ÿ"
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


def test_config_paths() -> None:
    """Verifica que la configuración devuelva rutas Path independientes."""
    config = load_config()
    assert isinstance(config.input_file, Path)
    assert isinstance(config.output_file, Path)
    assert config.input_file != config.output_file


def test_main_runs_without_input_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Comprueba el error controlado sin archivos reales del usuario.

    Args:
        tmp_path: Directorio temporal.
        monkeypatch: Sustitución de configuración.
        capsys: Captura de salida.
    """
    import main as application

    monkeypatch.setattr(application, "load_config", lambda: SimulationConfig(
        tmp_path / "ausente.txt", tmp_path / "salida.txt",
    ))
    application.main()
    output = capsys.readouterr().out
    assert "[ERROR] No se pudo leer" in output
    assert "AWGN" not in output
    assert list(tmp_path.iterdir()) == []
