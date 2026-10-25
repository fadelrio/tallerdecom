"""Contratos de energías, errores e histograma; sin cálculos implementados."""

import numpy as np

from common.data_types import (
    Constellation, EnergyStatistics, ErrorRates, ModulatedData, SymbolStatistics,
)
from config import ModulationConfig


def estimate_energies(
    symbols: np.ndarray, config: ModulationConfig,
) -> EnergyStatistics:
    """Estimará las energías medias de la secuencia transmitida.

    Args:
        symbols: Coordenadas reales no vacías (N, D), incluyendo el símbolo final.
        config: Orden de modulación y tasa de código compartidos.

    Returns:
        Energías medias por símbolo, bit de canal y bit de información.

    Raises:
        NotImplementedError: Mientras la estimación esté pendiente.
        ValueError: En la futura implementación, para vacío, dimensiones o
            configuración inválidas, o coordenadas no finitas.

    Notes:
        Usar la energía en una base ortonormal. No suponer equiprobabilidad en
        la muestra ni forzar el resultado al Eb nominal de la configuración.
    """
    raise NotImplementedError("Estimación de energías pendiente.")


def theoretical_energies(config: ModulationConfig) -> EnergyStatistics:
    """Obtendrá la referencia energética para símbolos equiprobables.

    Args:
        config: Orden, energía de información y tasa de código.

    Returns:
        Energías teóricas por símbolo, bit de canal y bit de información.

    Raises:
        NotImplementedError: Mientras la referencia esté pendiente.
        ValueError: En la futura implementación, para configuración inválida.

    Notes:
        Diferenciar Eb de información y Ec del flujo de canal. Una muestra
        PAM no equiprobable puede diferir de esta referencia.
    """
    raise NotImplementedError("Energías teóricas pendientes.")


def estimate_symbol_error_rate(
    transmitted: np.ndarray, decided: np.ndarray,
) -> float:
    """Comparará símbolos transmitidos con símbolos decididos.

    Args:
        transmitted: Coordenadas de la constelación transmitidas (N, D).
        decided: Coordenadas decididas de la misma constelación (N, D).

    Returns:
        Frecuencia de símbolos distintos, entre cero y uno.

    Raises:
        NotImplementedError: Mientras la comparación esté pendiente.
        ValueError: En la futura implementación, para vacío, formas diferentes
            o coordenadas no finitas.

    Notes:
        Contar un símbolo erróneo aunque cambien varias coordenadas. Incluir
        el símbolo final con relleno. No recibir observaciones con ruido.
    """
    raise NotImplementedError("Estimación de SER pendiente.")


def estimate_bit_error_rate(transmitted: str, received: str) -> float:
    """Comparará las secuencias binarias transmitida y recuperada.

    Args:
        transmitted: Bits originales, sin relleno de modulación.
        received: Bits recuperados, con el relleno ya descartado.

    Returns:
        Frecuencia de bits distintos, entre cero y uno.

    Raises:
        NotImplementedError: Mientras la comparación esté pendiente.
        ValueError: En la futura implementación, para vacío, longitudes
            diferentes o caracteres distintos de '0' y '1'.

    Notes:
        Comparar flujos de la misma etapa, antes de decodificar Huffman.
    """
    raise NotImplementedError("Estimación de BER pendiente.")


def theoretical_error_rates(
    config: ModulationConfig, eb_n0_db: float,
) -> ErrorRates:
    """Obtendrá referencias de error para PAM y FSK coherentes en AWGN.

    Args:
        config: Constelación, etiquetamiento, energía y tasa de código.
        eb_n0_db: Relación Eb/N0 de información expresada en decibeles.

    Returns:
        SER y BER teóricas en las decisiones previas a decodificar el canal.

    Raises:
        NotImplementedError: Mientras las referencias estén pendientes.
        ValueError: En la futura implementación, para configuración inválida
            o relación Eb/N0 no finita.

    Notes:
        Suponer símbolos equiprobables, AWGN y FSK ortogonal coherente. Usar
        code_rate para interpretar Eb/N0, sin atribuir ganancia de un código
        que no se está decodificando. Documentar cualquier aproximación de BER
        y su dominio; el etiquetamiento puede afectar BER, no la geometría.
    """
    raise NotImplementedError("Probabilidades teóricas de error pendientes.")


def symbol_statistics(
    modulated: ModulatedData, constellation: Constellation,
) -> SymbolStatistics:
    """Preparará los conteos y frecuencias de los símbolos transmitidos.

    Args:
        modulated: Símbolos transmitidos (N, D), incluyendo el símbolo final.
        constellation: Todas las coordenadas y etiquetas posibles.

    Returns:
        Etiquetas, conteos y frecuencias en el orden de la constelación,
        incluyendo ceros para símbolos no observados.

    Raises:
        NotImplementedError: Mientras el histograma esté pendiente.
        ValueError: En la futura implementación, para muestra vacía,
            constelación incompatible o símbolos ajenos a ella.

    Notes:
        No asumir equiprobabilidad ni emitir conclusiones sobre el histograma.
    """
    raise NotImplementedError("Estadísticas de símbolos pendientes.")
