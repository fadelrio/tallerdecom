
from common.data_types import ModulatedData
from common.data_types import EncodedSource
from config import ModulationConfig
from math import log2, sqrt
import numpy as np

def modulation(encoded: EncodedSource, Modulacion_config: ModulationConfig) -> ModulatedData:
    """Modula la fuente codificada según la configuración de modulación.

    Args:
        encoded: Fuente codificada con bits.
        config: Configuración de modulación (M y tipo).

    Returns:
        Objeto ModulatedData con los símbolos modulados.
    """
    # Aquí se implementaría la lógica de modulación según el tipo y M.
    # Por ejemplo, para PAM o FSK, se mapearían los bits a símbolos en la constelación.
    # Esta función es un placeholder y debe ser completada según los requisitos específicos.
    
    if(Modulacion_config.tipo == 'PAM'):
        # Implementar modulación PAM
        result = modulation_PAM(encoded, Modulacion_config.M, Modulacion_config.Eb)
    elif(Modulacion_config.tipo == 'FSK'):
        # Implementar modulación FSK
        result = modulation_FSK(encoded, Modulacion_config.M, Modulacion_config.Eb)

    return result

def modulation_PAM(encoded: EncodedSource, M: int, Eb: float = 1.0) -> ModulatedData:
    """Implementa la modulación MPAM con mapeo Gray y energía de bit Eb.

    Las coordenadas de los símbolos son ±E0, ±3*E0, ..., ±(M-1)*E0, con E0
    elegido de modo que Es = log2(M) * Eb. La distancia mínima entre símbolos
    vecinos es 2*E0.

    Si la cantidad de bits no es múltiplo de log2(M), se completa con ceros al
    final y se informa la cantidad agregada en `padding_bits`.

    Args:
        encoded: Fuente codificada con bits.
        M: Cantidad de símbolos en la constelación (potencia de 2).
        Eb: Energía de bit; Es = log2(M) * Eb.

    Returns:
        Objeto ModulatedData con los símbolos modulados en PAM (matriz (N, 1)).
    """
    k = int(log2(M)) #bits por símbolo

    # Relleno con ceros para completar el último bloque de k bits
    padding = (-len(encoded.bits)) % k
    bits = encoded.bits + "0" * padding

    # Coordenada del símbolo más cercano al origen, tal que Es = k * Eb
    E0 = sqrt(3 * k * Eb / (M**2 - 1))

    # Tabla: palabra Gray -> coordenada (niveles ordenados de menor a mayor)
    tabla = {}
    for idx in range(M):
        gray = idx ^ (idx >> 1)
        tabla[format(gray, f"0{k}b")] = (2 * idx - (M - 1)) * E0

    symbols = np.array(
        [tabla[bits[i:i + k]] for i in range(0, len(bits), k)]
    ).reshape(-1, 1)  # (N, 1): D = 1

    return ModulatedData(symbols=symbols, padding_bits=padding)


def modulation_FSK(encoded: EncodedSource, M: int, Eb: float = 1.0) -> ModulatedData:
    """Implementa la modulación FSK para los bits codificados.

    Args:
        encoded: Fuente codificada con bits.
        M: Cantidad de símbolos en la constelación.

    Returns:
        Objeto ModulatedData con los símbolos modulados en FSK.
    """
    # Aquí se implementaría la lógica específica de modulación FSK.
    # Esta función es un placeholder y debe ser completada según los requisitos específicos.
    raise(NotImplementedError("La modulación FSK aún no está implementada."))