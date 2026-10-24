"""Configuración inicial de los apartados A y B."""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class SimulationConfig:
    """Rutas del sistema de comunicaciones.

    Attributes:
        input_file: Ruta del archivo de entrada .txt UTF-8.
        output_file: Ruta del futuro archivo recibido .txt UTF-8.
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
    return SimulationConfig(root / "res/muchos_martin_fierro.txt", root / "res/output.txt")

###                 EMPEZAMOS PARTE D   (24/10)       ###


@dataclass
class ModulationConfig:
    """Configuración de la modulación.

    Attributes:
        M: Cantidad de símbolos en la constelación.
        tipo: Tipo de modulación (por ejemplo, 'PSK', 'QAM').
        Eb: Energía de bit; Es = log2(M) * Eb.
    """

    M: int
    tipo: str
    Eb: float = 1.0  # Energía de bit, por defecto 1.0

def load_modulation_config(M: int, tipo: str, Eb: float = 1.0) -> ModulationConfig:
    """Carga la configuración de modulación según los parámetros dados. Corrobora que M sea
    potencia de 2 y que sea a lo sumo 16. También corrobora que tipo sea 'PAM' o 'FSK'
    Corrobora que Eb > 0

    Args:
        M: Cantidad de símbolos en la constelación.
        tipo: Tipo de modulación (por ejemplo, 'PSK', 'QAM').

    Returns:
        Una instancia de ModulationConfig con los parámetros especificados.
    """
    if M <= 0 or (M & (M - 1)) != 0 or M > 16:
        raise ValueError("M debe ser una potencia de 2 y a lo sumo 16.")
    if tipo not in ['PAM', 'FSK']:
        raise ValueError("tipo debe ser 'PAM' o 'FSK'.")
    if Eb <= 0:
        raise ValueError("Eb debe ser mayor que 0.")
    return ModulationConfig(M = M, tipo = tipo, Eb = Eb)
