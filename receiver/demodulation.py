"""Contratos de demodulación; las decisiones quedan por implementar."""

from common.data_types import DemodulatedData, ModulatedData
from config import ModulationConfig


def demodulation(
    modulated: ModulatedData, config: ModulationConfig,
) -> DemodulatedData:
    """Seleccionará el demodulador y recuperará la secuencia binaria.

    Args:
        modulated: Coordenadas recibidas (N, D) y cantidad de bits de relleno.
        config: Parámetros compartidos con el transmisor.

    Returns:
        Símbolos decididos (N, D) y bits sin relleno. La entrada vacía válida
        devolverá una matriz (0, D) y una cadena vacía.

    Raises:
        NotImplementedError: Mientras el selector esté pendiente.
        ValueError: En la futura implementación, para configuración, dimensiones
            o relleno incompatibles, o coordenadas no finitas.

    Notes:
        Delegar en PAM o FSK y aplicar el retiro de relleno una sola vez.
        Las funciones específicas tendrán el mismo contrato de salida.
    """
    raise NotImplementedError("Selector de demodulación pendiente.")


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
    raise NotImplementedError("Demodulación PAM pendiente.")


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
    raise NotImplementedError("Demodulación FSK pendiente.")
