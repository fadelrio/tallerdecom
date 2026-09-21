"""Lectura, escritura y comparación de texto UTF-8."""

from pathlib import Path

from common.data_types import FileComparison


def read_file(path: Path) -> str:
    """Lee texto UTF-8 sin normalizar saltos de línea ni eliminar el BOM.

    Args:
        path: Ruta del archivo de texto.

    Returns:
        Texto completo, incluidos todos sus caracteres de control.

    Raises:
        OSError: Si el archivo no puede leerse.
        UnicodeDecodeError: Si el contenido no es UTF-8 válido.
    """
    # newline='' preserva CR, LF y CRLF tal como aparecen en el archivo.
    with path.open("r", encoding="utf-8", newline="") as file:
        return file.read()


def write_file(path: Path, data: str) -> None:
    """Escribe texto UTF-8 sin traducir saltos de línea.

    Args:
        path: Ruta de salida.
        data: Texto recuperado por el receptor.

    Raises:
        OSError: Si el archivo no puede escribirse.
        UnicodeEncodeError: Si el texto no puede representarse en UTF-8.
    """
    with path.open("w", encoding="utf-8", newline="") as file:
        file.write(data)


def compare_data(original: str, received: str) -> FileComparison:
    """Compara exactamente dos textos, sin normalizarlos.

    Args:
        original: Texto de entrada.
        received: Texto recuperado.

    Returns:
        Igualdad y longitudes en caracteres (puntos de código Unicode).
    """
    return FileComparison(original == received, len(original), len(received))
