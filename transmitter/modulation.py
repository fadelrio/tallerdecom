"""Modulación PAM y FSK en el espacio de señales."""
from common.constellations import build_constellation
from common.data_types import ModulatedData
from common.data_types import EncodedSource
from config import ModulationConfig
from math import log2
import numpy as np

def modulation(encoded: EncodedSource, Modulacion_config: ModulationConfig) -> ModulatedData:
    """Modula la fuente codificada según la configuración de modulación.

    Args:
        encoded: Fuente codificada con bits.
        Modulacion_config: Configuración de modulación (M y tipo).

    Returns:
        Objeto ModulatedData con los símbolos modulados.
    """
    
    if(Modulacion_config.tipo == 'PAM'):
        result = modulation_PAM(encoded, Modulacion_config)
    elif(Modulacion_config.tipo == 'FSK'):
        result = modulation_FSK(encoded, Modulacion_config)

    return result

def modulation_PAM(encoded: EncodedSource, config: ModulationConfig) -> ModulatedData:
    """Implementa la modulación MPAM con el etiquetado configurado.

    Las coordenadas de los símbolos son ±E0, ±3*E0, ..., ±(M-1)*E0, con E0
    elegido de modo que Es = log2(M) * Eb * code_rate. La distancia mínima entre símbolos
    vecinos es 2*E0.

    Si la cantidad de bits no es múltiplo de h = log2(M), se descartan
    los bits sobrantes.

    Args:
        encoded: Fuente codificada con bits.
        config: Configuración de modulación (M, Eb, constelación y etiquetas).

    Returns:
        Objeto ModulatedData con los símbolos modulados en PAM (matriz (N, 1)).
    """
    constellation = build_constellation(config)
    k = int(log2(config.M)) #bits por símbolo

    descartar = len(encoded.bits) % k # Resto de la división entera por k

    flag_descarte = False
    if descartar:
        bits = encoded.bits[:-descartar] #se descartan los últimos bits
        flag_descarte = True
    else:
        bits = encoded.bits

    symbols = []

    for i in range(0, len(bits), k):

        etiqueta = bits[i:i+k] #tomar un bloque de k bits

        indice = constellation.labels.index(etiqueta)

        simbolo = constellation.symbols[indice]

        symbols.append(simbolo)

    symbols = np.array(symbols)

    return ModulatedData(symbols=symbols, flag_descarte=flag_descarte)


def modulation_FSK(encoded: EncodedSource, config: ModulationConfig) -> ModulatedData:
    """Implementa FSK ortogonal en coordenadas con el etiquetado configurado.

    La energía de símbolo es Es = log2(M) * Eb * code_rate, por lo que la norma de cada
    vector es sqrt(Es).

    Args:
        encoded: Fuente codificada con bits.
        config: Configuración de modulación y etiquetado.

    Returns:
        Símbolos (N, M). N es la cantidad de símbolos. Si la cantidad de bits no es múltiplo de 
        k = log2(M), se descartan los sobrantes.

    """
    constellation = build_constellation(config)
    k = int(log2(config.M)) #bits por símbolo

    descartar = len(encoded.bits) % k # Resto de la división entera por k

    flag_descarte = False
    if descartar:
        bits = encoded.bits[:-descartar] #se descartan los últimos bits
        flag_descarte = True
    else:
        bits = encoded.bits

    symbols = []

    for i in range(0, len(bits), k):

        etiqueta = bits[i:i+k] #tomar un bloque de k bits

        indice = constellation.labels.index(etiqueta)

        simbolo = constellation.symbols[indice]

        symbols.append(simbolo)

    symbols = np.array(symbols)
    
    return ModulatedData(symbols=symbols, flag_descarte=flag_descarte)
