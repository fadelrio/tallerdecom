"""Contrato de construcción de constelaciones PAM y FSK; pendiente."""

from common.data_types import Constellation
from config import ModulationConfig


def build_constellation(config: ModulationConfig) -> Constellation:
    """Construirá coordenadas y etiquetas para el esquema seleccionado.

    Args:
        config: Configuración PAM/FSK, orden, Eb, etiquetamiento y tasa.

    Returns:
        Coordenadas (M, 1) para PAM o (M, M) para FSK ortogonal coherente,
        con una etiqueta de log2(M) bits por fila. Los niveles PAM estarán
        ordenados de menor a mayor y los símbolos FSK por eje de la base.

    Raises:
        NotImplementedError: Mientras la construcción esté pendiente.
        ValueError: En la futura implementación, si la configuración es inválida.

    Notes:
        Normalizar según Eb de información y code_rate, suponiendo símbolos
        equiprobables. Admitir Gray y binario. Las etiquetas Gray seguirán
        el código reflejado en el orden de las filas. No generar ondas.
        Debe ser la definición común para transmisor, receptor y gráficos;
        su conexión con el modulador PAM existente queda pendiente.
    """
    raise NotImplementedError("Construcción de constelaciones pendiente.")
