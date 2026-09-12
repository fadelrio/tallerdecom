"""Configuración inicial de los apartados A y B."""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class SimulationConfig:
    """Rutas del sistema de comunicaciones.

    Attributes:
        input_file: Ruta del archivo de entrada binario.
        output_file: Ruta del futuro archivo recibido binario.
    """

    input_file: Path
    output_file: Path


def load_config() -> SimulationConfig:
    """Devuelve una configuración de ejemplo.

    Returns:
        Rutas de entrada y salida relativas a la raíz del proyecto.

    Notes:
        No lee ni crea archivos. Las rutas pueden editarse aquí.
    """
    root = Path(__file__).resolve().parent
    return SimulationConfig(root / "entrada.bin", root / "recibido.bin")
