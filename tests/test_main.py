"""Pruebas de lectura y rechazo controlado en el orquestador."""

from pathlib import Path

import pytest

import main as application
from common.file_utils import read_file
from config import SimulationConfig


@pytest.mark.parametrize("data", ['', '\x00ÿ\r\n'])
def test_read_text(tmp_path: Path, data: str) -> None:
    """Verifica lectura exacta sin transformaciones de texto.

    Args:
        tmp_path: Directorio temporal de pytest.
        data: Contenido textual del archivo.
    """
    path = tmp_path / "entrada.txt"
    path.write_bytes(data.encode("utf-8"))
    assert read_file(path) == data


def test_empty_file_stops_before_huffman(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Rechaza el vacío sin llamar a Huffman ni modificar la salida.

    Args:
        tmp_path: Directorio temporal de pytest.
        monkeypatch: Sustitución temporal de configuración y Huffman.
        capsys: Captura de mensajes del principal.
    """
    source = tmp_path / "entrada.txt"
    output = tmp_path / "salida.txt"
    source.write_text('')
    output.write_text('conservar')
    monkeypatch.setattr(application, "load_config",
                        lambda: SimulationConfig(source, output))

    def unexpected_huffman(probabilities: dict[str, float]) -> None:
        """Falla si el orquestador deja llegar una fuente vacía a Huffman."""
        pytest.fail("No debe llamarse a Huffman para un archivo vacío")

    monkeypatch.setattr(application, "build_huffman_code", unexpected_huffman)
    application.main()
    assert "Archivo vacío" in capsys.readouterr().out
    assert output.read_text() == 'conservar'


def test_nonempty_file_runs_transmitter(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Ejecuta el transmisor real sin invocar las etapas pendientes.

    Args:
        tmp_path: Directorio temporal de pytest.
        monkeypatch: Sustitución temporal de las rutas configuradas.
        capsys: Captura de mensajes del principal.
    """
    source = tmp_path / "entrada.txt"
    output = tmp_path / "salida.txt"
    source.write_text('\x00ÿ\x00\n', encoding='utf-8')
    monkeypatch.setattr(application, "load_config",
                        lambda: SimulationConfig(source, output))
    application.main()
    output_text = capsys.readouterr().out
    assert "Fuente codificada: 6 bits" in output_text
    assert "6. COMPARACIÓN DE ARCHIVOS" in output_text
    assert "Texto idéntico: True" in output_text
    assert "AWGN" not in output_text
    assert read_file(output) == read_file(source)


def test_utf8_file_round_trip(tmp_path: Path) -> None:
    """Preserva BOM, acentos y CR/LF sin depender del sistema operativo.

    Args:
        tmp_path: Directorio temporal de pruebas.
    """
    from common.file_utils import write_file, compare_data

    text = "\ufeffáñ\r\ntexto\rfin\n\t世界"
    source = tmp_path / "entrada.txt"
    output = tmp_path / "recibido.txt"
    source.write_bytes(text.encode("utf-8"))
    read = read_file(source)
    assert read == text
    write_file(output, read)
    assert output.read_bytes() == source.read_bytes()
    result = compare_data(text, read_file(output))
    assert result.identical
    assert result.original_size == len(text)


def test_invalid_utf8(tmp_path: Path) -> None:
    """No reemplaza silenciosamente caracteres de un archivo inválido.

    Args:
        tmp_path: Directorio temporal de pruebas.
    """
    source = tmp_path / "invalido.txt"
    source.write_bytes(b"\xff")
    with pytest.raises(UnicodeDecodeError):
        read_file(source)


@pytest.mark.parametrize("filename", ["texto propio.txt", "pg12345.txt"])
def test_cli_local_sources(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str], filename: str,
) -> None:
    """Procesa archivos seleccionados sin depender de Internet.

    Args:
        tmp_path: Directorio temporal.
        monkeypatch: Sustituye argumentos de terminal.
        capsys: Captura las tablas impresas.
        filename: Nombre propio o con el estilo de una descarga Gutenberg.
    """
    import sys

    source = tmp_path / filename
    output = tmp_path / "recibido.txt"
    # Encabezado y controles se conservan; no se limpia la obra implícitamente.
    text = "*** START OF THE PROJECT GUTENBERG EBOOK ***\r\nEspaña\r\n"
    source.write_bytes(text.encode("utf-8"))
    monkeypatch.setattr(sys, "argv", [
        "main.py", "--input", str(source), "--output", str(output),
    ])
    application.cli()
    assert output.read_bytes() == source.read_bytes()
    assert "Texto idéntico: True" in capsys.readouterr().out
