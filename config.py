"""Configuración de fuente y contratos para la futura etapa de modulación."""

from dataclasses import dataclass
from math import isfinite
from numbers import Integral, Real
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


@dataclass
class ModulationConfig:
    """Configuración de la modulación.

    Attributes:
        M: Cantidad de símbolos en la constelación.
        tipo: Esquema asignado al grupo: 'PAM' o 'FSK'.
        Eb: Energía media de bit de información; por defecto unitaria.
        labeling: Etiquetamiento solicitado: 'gray' o 'binary'.
        code_rate: Tasa de codificación de canal k/n; 1.0 sin codificación.

    Notes:
        No valida sus campos. PAM y el selector actuales todavía no aplican
        labeling ni code_rate: conservan Gray y el caso sin código de canal.
        Su aplicación en los moduladores queda pendiente. El cargador y la
        simulación con modulación ya usan validate_modulation_config.
    """

    M: int
    tipo: str
    Eb: float = 1.0  # Energía de bit, por defecto 1.0
    labeling: str = "gray"
    code_rate: float = 1.0


def load_modulation_config(M: int, tipo: str, Eb: float = 1.0) -> ModulationConfig:
    """Construye y valida una configuración con las etiquetas y tasa por defecto.

    Args:
        M: Cantidad de símbolos en la constelación.
        tipo: 'PAM' o 'FSK'.
        Eb: Energía de bit solicitada.

    Returns:
        Una instancia de ModulationConfig con los parámetros especificados.

    Raises:
        TypeError: Si los parámetros tienen tipos incompatibles.
        ValueError: Si los parámetros quedan fuera del dominio admitido.

    Notes:
        labeling y code_rate toman los valores por defecto de la dataclass;
        pueden especificarse al construir ModulationConfig directamente.
    """
    config = ModulationConfig(M=M, tipo=tipo, Eb=Eb)
    validate_modulation_config(config)
    return config


def validate_modulation_config(config: ModulationConfig) -> None:
    """Valida los parámetros admitidos, sin modificar la configuración.

    Args:
        config: Esquema PAM/FSK, M, energía, etiquetamiento y tasa de código.

    Returns:
        None cuando la configuración sea válida.

    Raises:
        ValueError: Para M fuera de 2, 4, 8, 16,
            esquema o etiquetas desconocidos, Eb no finita o no positiva,
            y code_rate no finita o fuera de (0, 1].
        TypeError: Para tipos incompatibles; M debe ser entero y Eb y
            code_rate deben ser reales. No se admiten booleanos como números.

    Notes:
        Admite 'gray' y 'binary' en ambos esquemas. Verifica el dominio del
        contrato, no que todos los algoritmos solicitados estén implementados.
    """
    if not isinstance(config, ModulationConfig):
        raise TypeError("config debe ser una instancia de ModulationConfig.")
    if isinstance(config.M, bool) or not isinstance(config.M, Integral):
        raise TypeError("M debe ser un entero y no un booleano.")
    if config.M not in (2, 4, 8, 16):
        raise ValueError("M debe ser 2, 4, 8 o 16.")
    if not isinstance(config.tipo, str):
        raise TypeError("tipo debe ser una cadena.")
    if config.tipo not in ("PAM", "FSK"):
        raise ValueError("tipo debe ser 'PAM' o 'FSK'.")
    if not isinstance(config.labeling, str):
        raise TypeError("labeling debe ser una cadena.")
    if config.labeling not in ("gray", "binary"):
        raise ValueError("labeling debe ser 'gray' o 'binary'.")
    for name, value in (("Eb", config.Eb), ("code_rate", config.code_rate)):
        if isinstance(value, bool) or not isinstance(value, Real):
            raise TypeError(f"{name} debe ser un número real y no un booleano.")
        try:
            finite = isfinite(value)
        except OverflowError:
            finite = False
        if not finite or value <= 0:
            raise ValueError(f"{name} debe ser finito y mayor que cero.")
    if config.code_rate > 1:
        raise ValueError("code_rate debe pertenecer al intervalo (0, 1].")
