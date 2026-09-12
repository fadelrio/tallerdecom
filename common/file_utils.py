"""Contratos de entrada, salida y comparación; independientes de Huffman."""

from pathlib import Path

from common.data_types import FileComparison


def read_file(path: Path) -> bytes:
    """Leerá el archivo de entrada en modo binario.

    Args:
        path: Ruta del archivo que se leerá.

    Returns:
        Contenido completo como bytes, sin interpretación textual.

    Raises:
        NotImplementedError: La lectura está pendiente.
    """
    raise NotImplementedError("Lectura binaria pendiente.")


def write_file(path: Path, data: bytes) -> None:
    """Escribirá los bytes recibidos en modo binario.

    Args:
        path: Ruta del archivo de destino.
        data: Secuencia de bytes recibida.

    Raises:
        NotImplementedError: La escritura está pendiente.

    Notes:
        Este placeholder no crea ni modifica archivos.
    """
    raise NotImplementedError("Escritura binaria pendiente.")


def compare_data(original: bytes, received: bytes) -> FileComparison:
    """Comparará los contenidos binarios original y recibido.

    Args:
        original: Bytes de entrada.
        received: Bytes reconstruidos.

    Returns:
        Igualdad exacta de contenidos y tamaño de cada secuencia en bytes.

    Raises:
        NotImplementedError: La comparación está pendiente.
    """
    raise NotImplementedError("Comparación de datos pendiente.")
