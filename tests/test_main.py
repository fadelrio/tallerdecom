"""Pruebas de lectura y rechazo controlado en el orquestador."""

from pathlib import Path

import pytest

import main as application
from common.file_utils import read_file
from config import SimulationConfig


@pytest.mark.parametrize("data", [b"", b"\x00\xff\r\n"])
def test_read_binary(tmp_path: Path, data: bytes) -> None:
    """Verifica lectura exacta sin transformaciones de texto.

    Args:
        tmp_path: Directorio temporal de pytest.
        data: Contenido binario del archivo.
    """
    path = tmp_path / "entrada.bin"
    path.write_bytes(data)
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
    source = tmp_path / "entrada.bin"
    output = tmp_path / "salida.bin"
    source.write_bytes(b"")
    output.write_bytes(b"conservar")
    monkeypatch.setattr(application, "load_config",
                        lambda: SimulationConfig(source, output))

    def unexpected_huffman(probabilities: dict[int, float]) -> None:
        """Falla si el orquestador deja llegar una fuente vacía a Huffman."""
        pytest.fail("No debe llamarse a Huffman para un archivo vacío")

    monkeypatch.setattr(application, "build_huffman_code", unexpected_huffman)
    application.main()
    assert "Archivo vacío" in capsys.readouterr().out
    assert output.read_bytes() == b"conservar"


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
    source = tmp_path / "entrada.bin"
    output = tmp_path / "salida.bin"
    source.write_bytes(b"\x00\xff\x00\n")
    monkeypatch.setattr(application, "load_config",
                        lambda: SimulationConfig(source, output))
    application.main()
    assert "Fuente codificada: 6 bits" in capsys.readouterr().out
    assert not output.exists()
