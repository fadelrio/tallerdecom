"""PAM existente y contrato pendiente de FSK; sin cambios en los algoritmos."""
from common.data_types import ModulatedData
from common.data_types import EncodedSource
from config import ModulationConfig
from math import log2, sqrt
import numpy as np

def modulation(encoded: EncodedSource, Modulacion_config: ModulationConfig) -> ModulatedData:
    """Modula la fuente codificada según la configuración de modulación.

    Args:
        encoded: Fuente codificada con bits.
        Modulacion_config: Configuración de modulación (M y tipo).

    Returns:
        Objeto ModulatedData con los símbolos modulados.
    """
    # Pendiente: validar con validate_modulation_config, aplicar labeling y
    # code_rate y compartir build_constellation. Se conserva el selector actual.
    
    if(Modulacion_config.tipo == 'PAM'):
        # Implementar modulación PAM
        result = modulation_PAM(encoded, Modulacion_config)
    elif(Modulacion_config.tipo == 'FSK'):
        # Implementar modulación FSK
        result = modulation_FSK(encoded, Modulacion_config)

    return result

def modulation_PAM(encoded: EncodedSource, config: ModulationConfig) -> ModulatedData:
    """Implementa la modulación MPAM con mapeo Gray y energía de bit Eb.

    Las coordenadas de los símbolos son ±E0, ±3*E0, ..., ±(M-1)*E0, con E0
    elegido de modo que Es = log2(M) * Eb. La distancia mínima entre símbolos
    vecinos es 2*E0.

    Si la cantidad de bits no es múltiplo de h = log2(M), se descartan
    los bits sobrantes.

    Args:
        encoded: Fuente codificada con bits.
        config: Configuración de modulación (M, Eb, constelación y etiquetas).

    Returns:
        Objeto ModulatedData con los símbolos modulados en PAM (matriz (N, 1)).
    """
    k = int(log2(config.M)) #bits por símbolo

    descartar = len(encoded.bits) % k # Resto de la división entera por k

    if descartar:
        bits = encoded.bits[:-descartar] #se descartan los últimos bits
    else:
        bits = encoded.bits

    symbols = []

    for i in range(0, len(bits), k):

        etiqueta = bits[i:i+k] #tomar un bloque de k bits

        indice = config.etiquetas.index(etiqueta) #buscar a qué indicie corresponde en el vector de etiquetas

        simbolo = config.constelacion[indice] #en ese mismo índicse se guarda el vector al que corresponde

        symbols.append(simbolo)

    symbols = np.array(symbols)

    return ModulatedData(symbols=symbols)


def modulation_FSK(encoded: EncodedSource, config: ModulationConfig) -> ModulatedData:
    """Implementará FSK ortogonal mediante coordenadas, sin formas de onda. 
    Los signos se asignan por código binario.
    La energía de símbolo es Es = log2(M) * Eb, por lo que la norma de cada 
    vector es sqrt(Es).

    Args:
        encoded: Fuente codificada con bits.
        M: Cantidad de símbolos en la constelación.
        Eb: Energía por bit del flujo de entrada; por defecto unitaria.

    Returns:
        Símbolos (N, M). N es la cantidad de símbolos. Si la cantidad de bits no es múltiplo de 
        k = log2(M), se descartan los sobrantes.

    Notes:
        Conservar la firma existente. El caso básico usará Gray reflejado por
        orden de eje de base, como build_constellation con valores por defecto.
        La selección binaria y la tasa de canal quedan por integrar en el
        selector y las interfaces de los moduladores. No implementar portadoras.
    """
    k = int(log2(config.M)) #bits por símbolo

    descartar = len(encoded.bits) % k # Resto de la división entera por k

    if descartar:
        bits = encoded.bits[:-descartar] #se descartan los últimos bits
    else:
        bits = encoded.bits

    symbols = []

    for i in range(0, len(bits), k):

        etiqueta = bits[i:i+k] #tomar un bloque de k bits

        indice = config.etiquetas.index(etiqueta) #buscar a qué indicie corresponde en el vector de etiquetas

        simbolo = config.constelacion[indice] #en ese mismo índicse se guarda el vector al que corresponde

        symbols.append(simbolo)

    symbols = np.array(symbols)
    
    return ModulatedData(symbols=symbols)
