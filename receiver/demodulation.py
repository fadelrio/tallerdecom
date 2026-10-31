"""Contratos de demodulación; las decisiones quedan por implementar."""

from common.data_types import DemodulatedData, ModulatedData
from config import ModulationConfig
import numpy as np


def demodulation(
    modulated: ModulatedData, config: ModulationConfig,
) -> DemodulatedData:
    """Seleccionará el demodulador y recuperará la secuencia binaria.

    Args:
        modulated: Coordenadas recibidas (N, D) y cantidad de bits de relleno.
        config: Parámetros compartidos con el transmisor.

    Returns:
        Símbolos decididos (N, D) y bits sin relleno. Podría devolverse solo la 
        tira de bits, pero puede ser útil conservar los símbolos obtenidos en el receptor. 
        La entrada vacía válida devolverá una matriz (0, D) y una cadena vacía.

    Raises:
        NotImplementedError: Mientras el selector esté pendiente.
        ValueError: En la futura implementación, para entradas incompatibles.

    Notes:
        Delegar en PAM o FSK.
        Las funciones específicas tendrán el mismo contrato de salida.
    """
    if config.tipo == "PAM":
        return demodulation_PAM(modulated, config)
    elif config.tipo == "FSK":
        return demodulation_FSK(modulated, config)
    else:
        raise ValueError(
            f"La modulación debe ser 'PAM' o 'FSK', no '{config.tipo}'."
        )


def demodulation_PAM(
    modulated: ModulatedData, config: ModulationConfig,
) -> DemodulatedData:
    """Decidirá símbolos PAM y recuperará sus etiquetas binarias.

    Args:
        modulated: Coordenadas recibidas (N, 1), con metadato de relleno.
        config: Configuración PAM usada en el transmisor.

    Returns:
        N símbolos de la constelación y la cadena binaria sin relleno.

    Raises:
        NotImplementedError: Mientras el demodulador esté pendiente.
        ValueError: En la futura implementación, para entradas incompatibles.

    Notes:
        Usar la constelación común y su etiquetamiento. En empates de distancia,
        elegir la primera fila de la constelación. Admitir entrada vacía válida.
        No decodificar Huffman ni comparar directamente coordenadas con ruido.
    """
    simbolos_ruidosos = modulated.symbols
    simbolo_decidido = []
    bits = ""
    for symbol in simbolos_ruidosos:
        distances = [abs(symbol - s) for s in config.constelacion]# Calcular la distancia a cada símbolo de la constelación
        
        closest_index = distances.index(min(distances))# Encontrar el índice del símbolo más cercano

        simbolo_decidido.append(config.constelacion[closest_index])# Obtener el símbolo más cercano de la constelación
        
        bits += config.etiquetas[closest_index]# Obtener la etiqueta correspondiente

    simbolo_decidido = np.array(simbolo_decidido)  # Convertir la lista de símbolos decididos a un array de NumPy
    
    return DemodulatedData(symbols=simbolo_decidido, bits=bits)    


def demodulation_FSK(
    modulated: ModulatedData, config: ModulationConfig,
) -> DemodulatedData:
    """Decidirá símbolos de FSK ortogonal con recepción coherente.

    Args:
        modulated: Coordenadas recibidas (N, M), con metadato de relleno.
        config: Configuración FSK usada en el transmisor.

    Returns:
        N símbolos de la constelación y la cadena binaria sin relleno.

    Raises:
        NotImplementedError: Mientras el demodulador esté pendiente.
        ValueError: En la futura implementación, para entradas incompatibles.

    Notes:
        Usar la constelación común. En empates elegir su primera fila.
        Admitir entrada vacía válida. No sintetizar ni procesar portadoras.
    """
    symbolos_ruidosos = modulated.symbols
    simbolo_decidido = []
    bits = ""
    for symbol in symbolos_ruidosos:
        distances = [np.linalg.norm(symbol - s) for s in config.constelacion]# Calcular la distancia a cada símbolo de la constelación
        
        closest_index = distances.index(min(distances))# Encontrar el índice del símbolo más cercano

        simbolo_decidido.append(config.constelacion[closest_index])# Obtener el símbolo más cercano de la constelación
        
        bits += config.etiquetas[closest_index]# Obtener la etiqueta correspondiente

    simbolo_decidido = np.array(simbolo_decidido)  # Convertir la lista de símbolos decididos a un array de NumPy

    return DemodulatedData(symbols=simbolo_decidido, bits=bits)
