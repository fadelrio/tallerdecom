

from common.data_types import ChannelConfig, ModulatedData
from config import ModulationConfig
import numpy as np

def channel_effects(datos_modulados: ModulatedData, config: ModulationConfig, channel_config: ChannelConfig) -> ModulatedData:
    """Aplica los efectos del canal a los datos modulados.

    Args:
        datos_modulados: Datos modulados.
        config: Configuración de modulación.
        channel_config: Configuración del canal.
    
    Returns: 
        Datos modulados con ruido aplicado.
        A futuro se incluirán otros efectos de canal como desvanecimiento, interferencia, etc.
    """

    # Extraer la densidad espectral de potencia del ruido del canal
    N0 = channel_config.N0

    # Generar ruido gaussiano con media 0 y varianza especificada
    ruido = np.random.normal(0, np.sqrt(N0/2), datos_modulados.symbols.shape)

    # Aplicar el ruido a los símbolos modulados
    simbolos_con_ruido = datos_modulados.symbols + ruido

    # Retornar los datos modulados con el ruido aplicado
    return ModulatedData(symbols=simbolos_con_ruido, flag_descarte=datos_modulados.flag_descarte)

