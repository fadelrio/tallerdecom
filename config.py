"""Configuración de fuente y contratos para la futura etapa de modulación."""

from dataclasses import dataclass
from math import isfinite, log2
from numbers import Integral, Real
from pathlib import Path
import numpy as np

from common.data_types import ChannelConfig


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
    return SimulationConfig(root / "res/textito.txt", root / "res/textito_output.txt")


@dataclass
class ModulationConfig:
    """Configuración de la modulación.

    Attributes:
        M: Cantidad de símbolos en la constelación.
        tipo: Esquema asignado al grupo: 'PAM' o 'FSK'.
        Eb: Energía media de bit de información; por defecto unitaria.
        code_rate: Tasa de codificación de canal k/n; 1.0 sin codificación.

    Notes:
        No valida sus campos. PAM y el selector actuales todavía no aplican
        labeling ni code_rate: conservan Gray y el caso sin código de canal.
        Su aplicación en los moduladores queda pendiente. El cargador y la
        simulación con modulación ya usan validate_modulation_config.
    """

    M: int
    tipo: str
    constelacion: np.ndarray # Matriz con los vectores de la constelación. Se genera en la configuración
    etiquetas: list[str] # Lista de etiquetas binarias asociadas a los símbolos de la constelación. Se genera en la configuración
    Eb: float = 1.0  # Energía de bit, por defecto 1.0
    #labeling: str = "gray" #¿Sacar? PAM usa gray y FSK binario, no se necesita saber más
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
    k = int(log2(M))
    if tipo == "PAM":
        E0 = np.sqrt(3 * k * Eb / (M**2 - 1))
        constelacion = np.array([[(-M + 1 + 2 * i) * E0] for i in range(M)]) #Vectores de la constelación
        etiquetas = [format(i ^ (i >> 1), f"0{k}b") for i in range(M)]  # Código Gray

    elif tipo == "FSK":
        norma = np.sqrt(k * Eb)
        constelacion = norma * np.eye(M)  # Base ortonormal para FSK
        etiquetas = [format(i, f"0{k}b") for i in range(M)]  # Código binario

    
    config = ModulationConfig(M=M, tipo=tipo, Eb=Eb, constelacion=constelacion, etiquetas=etiquetas)
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
    #if not isinstance(config.labeling, str):
    #    raise TypeError("labeling debe ser una cadena.")
    #if config.labeling not in ("gray", "binary"):
    #    raise ValueError("labeling debe ser 'gray' o 'binary'.")
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

def load_channel_config(ebno_dB: float, eb: float) -> ChannelConfig:
    """
    Crea la configuración del canal

    """
    ebno_veces = 10 ** (ebno_dB / 10)  # Convertir dB a lineal
    N0 = eb / ebno_veces  # Densidad espectral de potencia del ruido
    return ChannelConfig(ebno_dB=ebno_dB, N0=N0)
