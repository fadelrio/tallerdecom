"""Resultados conocidos de los datos del informe B."""

import pytest

from common.data_types import CodeStatistics, EncodedSource, HuffmanResult
from common.file_utils import compare_data
from common.report_utils import (
    build_coding_report, build_source_table, format_source_report,
)
from transmitter.source_analysis import analyze_source


def test_known_report() -> None:
    """Verifica tablas, unidades y totales con un código manual conocido."""
    text = "AAB\n"
    stats = analyze_source(text)
    code = HuffmanResult({"A": "0", "B": "10", "\n": "11"},
                         CodeStatistics(1.5, 1.5, 0.25, True))
    encoded = EncodedSource("001011")
    rows = build_source_table(stats, code)
    assert [(r.symbol, r.count, r.probability, r.huffman_code) for r in rows] == [
        ("\n", 1, 0.25, "11"), ("A", 2, 0.5, "0"), ("B", 1, 0.25, "10"),
    ]
    report = build_coding_report(stats, code, encoded)
    assert report.entropy == pytest.approx(1.5)
    assert report.minimum_length == 1.5
    assert report.variance == 0.25
    assert report.efficiency == 1.0
    assert report.huffman_total_bits == 6
    assert report.fixed_total_bits == 32
    assert report.fixed_representable
    output = format_source_report(text, text, stats, code, encoded,
                                  compare_data(text, text))
    assert "Verificación por pares: True" in output
    assert "Binario concatenado: 001011" in output
    assert "Decodificada: 'AAB\\n'" in output
    assert "Texto idéntico: True" in output


def test_non_cp1252_reference() -> None:
    """No presenta como realizable un código Windows-1252 para texto fuera de tabla."""
    stats = analyze_source("世")
    code = HuffmanResult({"世": "0"}, CodeStatistics(0.0, 1.0, 0.0, True))
    encoded = EncodedSource("0")
    report = build_coding_report(stats, code, encoded)
    assert not report.fixed_representable
    assert report.efficiency == 0.0
    output = format_source_report("世", "世", stats, code, encoded,
                                  compare_data("世", "世"))
    assert "Código fijo de 8 bits | No aplicable" in output


def test_markdown_special_characters() -> None:
    """Los caracteres del texto no rompen tablas ni bloques Markdown."""
    from transmitter.huffman import build_huffman_code
    from transmitter.source_encoder import encode_source

    text = "|```<&_\\\n"
    stats = analyze_source(text)
    code = build_huffman_code(stats.probabilities)
    encoded = encode_source(text, code.codebook)
    output = format_source_report(text, text, stats, code, encoded,
                                  compare_data(text, text))
    assert output.startswith("## DATOS DEL APARTADO B\n")
    assert "&#124;" in output
    assert "&lt;" in output
    assert "````text\n" in output
    # Tabla de seis columnas: sus datos no deben introducir separadores extra.
    table = output.split("### 1.")[1].split("### 2.")[0]
    for line in table.splitlines():
        if line.startswith("|"):
            assert line.count("|") == 7


def test_windows1252_punctuation() -> None:
    """La puntuación solicitada ocupa un byte por carácter en la referencia."""
    from transmitter.huffman import build_huffman_code
    from transmitter.source_encoder import encode_source

    text = "—‘’“”•™"
    stats = analyze_source(text)
    code = build_huffman_code(stats.probabilities)
    encoded = encode_source(text, code.codebook)
    report = build_coding_report(stats, code, encoded)
    assert report.fixed_encoding == "cp1252"
    assert report.fixed_representable
    assert report.fixed_total_bits == len(text.encode("cp1252")) * 8 == 56
    output = format_source_report(text, text, stats, code, encoded,
                                  compare_data(text, text))
    assert "Windows-1252" in output
    assert "No aplicable" not in output


def test_windows1252_unassigned_control() -> None:
    """Un valor Unicode menor que 256 no garantiza representación CP1252."""
    stats = analyze_source("\x81")
    code = HuffmanResult({"\x81": "0"}, CodeStatistics(0.0, 1.0, 0.0, True))
    report = build_coding_report(stats, code, EncodedSource("0"))
    assert not report.fixed_representable
