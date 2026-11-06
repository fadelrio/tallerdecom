"""Energías y tasas de error de modulación."""

from math import erfc, exp, expm1, isfinite, log, log1p, pi, sqrt
from numbers import Real

import numpy as np

from common.constellations import build_constellation
from common.data_types import (
    Constellation, EnergyStatistics, ErrorRates, ModulatedData, SymbolStatistics, BitErrorRate
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

    symbols = np.asarray(symbols)

    # Validar que la secuencia no esté vacía y tenga dos dimensiones.
    if symbols.ndim != 2 or symbols.shape[0] == 0 or symbols.shape[1] == 0:
        raise ValueError("La secuencia debe ser una matriz no vacía (N, D).")

    # Validar que las coordenadas sean finitas.
    if not np.all(np.isfinite(symbols)):
        raise ValueError("Las coordenadas deben ser finitas.")

    # Obtener los parámetros de la configuración.
    M = config.M
    Rc = config.code_rate

    if M <= 1 or Rc <= 0 or Rc > 1:
        raise ValueError("Configuración de modulación o tasa de código inválida.")

    # Energía media por símbolo.
    Es = np.mean(np.sum(symbols**2, axis=1))

    # Energía media por bit de canal e información.
    bits_por_simbolo = np.log2(M)
    
    #Ec = Es / bits_por_simbolo A completar después
    Ec = 1.0

    Eb = Es / bits_por_simbolo

    return EnergyStatistics(
        symbol_energy=float(Es),
        channel_bit_energy=float(Ec),
        bit_energy=float(Eb),
    ) 


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
    M = config.M
    Eb = config.Eb
    Rc = config.code_rate

    # Validar la configuración.
    if M <= 1 or not np.log2(M).is_integer():
        raise ValueError("M debe ser una potencia de 2 mayor que 1.")

    if not np.isfinite(Eb) or Eb <= 0:
        raise ValueError("Eb debe ser un valor positivo y finito.")

    if not np.isfinite(Rc) or Rc <= 0 or Rc > 1:
        raise ValueError("La tasa de código debe estar entre 0 y 1.")

    # Energías medias por bit de canal y por símbolo.
    Ec = Eb * Rc
    Es = Eb * np.log2(M)

    return EnergyStatistics(
        symbol_energy=float(Es),
        channel_bit_energy=float(Ec),
        bit_energy=float(Eb),
    )

    
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

    transmitted = np.asarray(transmitted)
    decided = np.asarray(decided)

    # Validar dimensiones y formas.
    if transmitted.ndim != 2 or decided.ndim != 2:
        raise ValueError("Ambas secuencias deben ser matrices (N, D).")

    if transmitted.shape != decided.shape:
        raise ValueError("Las secuencias deben tener la misma forma.")

    if transmitted.shape[0] == 0 or transmitted.shape[1] == 0:
        raise ValueError("Las secuencias no pueden estar vacías.")

    # Validar que las coordenadas sean numéricas y finitas.
    if not np.issubdtype(transmitted.dtype, np.number):
        raise ValueError("Los símbolos transmitidos deben ser numéricos.")

    if not np.issubdtype(decided.dtype, np.number):
        raise ValueError("Los símbolos decididos deben ser numéricos.")

    if not np.all(np.isfinite(transmitted)) or not np.all(np.isfinite(decided)):
        raise ValueError("Las coordenadas deben ser finitas.")

    # Comparar símbolos completos.
    errores = np.any(transmitted != decided, axis=1)

    return float(np.mean(errores))


def estimate_bit_error_rate(transmitted: str, received: str) -> BitErrorRate:    
    # Las cadenas pueden tener diferentes longitudes. Contamos los bits agregados como errores.
    """Compara las secuencias binarias transmitida y recibida.

    Args:
        transmitted: Bits originales, sin relleno de modulación.
        received: Bits recibidos.

    Returns:
        Frecuencia de bits distintos, entre cero y uno.

    Raises:
        NotImplementedError: Mientras la comparación esté pendiente.
        ValueError: En la futura implementación, para vacío, longitudes
            diferentes o caracteres distintos de '0' y '1'.

    Notes:
        Comparar flujos de la misma etapa, antes de decodificar Huffman.
    """
    # Validar que las secuencias no estén vacías y tengan la misma longitud.
    if not transmitted or not received:
        raise ValueError("Las secuencias no pueden estar vacías.")

    # Validar que las secuencias contengan solo '0' y '1'.
    if not all(bit in '01' for bit in transmitted):
        raise ValueError("La secuencia transmitida contiene caracteres inválidos.")

    if not all(bit in '01' for bit in received):
        raise ValueError("La secuencia recibida contiene caracteres inválidos.")

    # Contar bits distintos. El código debe ser legible.
    differing_bits = sum(t_bit != r_bit for t_bit, r_bit in zip(transmitted, received))
    total_bits = len(transmitted)
    error_rate = differing_bits / total_bits

    return BitErrorRate(
        error_rate=error_rate,
        bits_vistos=total_bits,
        bits_errados=differing_bits
    )

def theoretical_error_rates(
    config: ModulationConfig, eb_n0_db: float,
) -> ErrorRates:
    """Calcula la SER y BER de PAM y FSK ortogonal coherente en AWGN.

    Args:
        config: Constelación, etiquetamiento, energía y tasa de código.
        eb_n0_db: Relación Eb/N0 de información expresada en decibeles.

    Returns:
        SER y BER teóricas en las decisiones previas a decodificar el canal.

    Raises:
        TypeError: Si la configuración o Eb/N0 tienen tipos incompatibles.
        ValueError: Si la configuración es inválida o Eb/N0 no es finita.

    Notes:
        Para símbolos equiprobables, Es/N0 = log2(M) * code_rate * Eb/N0.
        En PAM se integran las regiones de decisión gaussianas y se ponderan
        por la distancia de Hamming. En FSK se integra numéricamente la
        probabilidad de que un eje incorrecto supere al eje transmitido.
    """
    if isinstance(eb_n0_db, bool) or not isinstance(eb_n0_db, Real):
        raise TypeError("eb_n0_db debe ser un número real.")
    if not isfinite(eb_n0_db):
        raise ValueError("eb_n0_db debe ser finito.")

    constellation = build_constellation(config)
    order = len(constellation.labels)
    bits_per_symbol = len(constellation.labels[0])
    log_es_n0 = log(bits_per_symbol * config.code_rate) + eb_n0_db / 10 * log(10)
    try:
        sqrt_es_n0 = exp(log_es_n0 / 2)
    except OverflowError:
        return ErrorRates(0.0, 0.0)

    if config.tipo == "PAM":
        half_spacing = sqrt_es_n0 * sqrt(6 / (order**2 - 1))
        return _pam_error_rates(constellation.labels, half_spacing)

    ser = _orthogonal_fsk_ser(order, sqrt_es_n0)
    # Por simetría todos los símbolos erróneos son igual de probables.
    # Cada bit difiere en M/2 de las M-1 etiquetas incorrectas.
    return ErrorRates(ser, ser * order / (2 * (order - 1)))


def _normal_tail(value: float) -> float:
    return erfc(value / sqrt(2)) / 2


def _pam_error_rates(labels: list[str], half_spacing: float) -> ErrorRates:
    """Suma las transiciones erróneas entre regiones PAM en unidades de sigma."""
    order = len(labels)
    words = [int(label, 2) for label in labels]
    symbol_errors = bit_errors = 0.0
    for sent, sent_word in enumerate(words):
        for decided, decided_word in enumerate(words):
            if sent == decided:
                continue
            offset = 2 * (decided - sent)
            lower = (offset - 1) * half_spacing if decided > 0 else float("-inf")
            upper = (offset + 1) * half_spacing if decided < order - 1 else float("inf")
            # Usar la cola positiva evita restar dos CDF casi iguales a uno.
            if decided < sent:
                lower, upper = -upper, -lower
            probability = _normal_tail(lower) - _normal_tail(upper)
            symbol_errors += probability
            bit_errors += probability * (sent_word ^ decided_word).bit_count()
    return ErrorRates(symbol_errors / order, bit_errors / (order * len(labels[0])))


def _orthogonal_fsk_ser(order: int, sqrt_es_n0: float) -> float:
    """Promedia la probabilidad de error condicionada al ruido del eje enviado."""
    if order == 2:
        return _normal_tail(sqrt_es_n0)

    nodes, weights = np.polynomial.legendre.leggauss(64)
    # El producto de la densidad y la cola de error se concentra cerca de
    # la mitad de la separación. El corte a 12 sigmas cubre ambas colas.
    half_separation = sqrt_es_n0 / sqrt(2)
    integral = 0.0
    for midpoint in (-6, 6):
        for node, weight in zip(nodes, weights):
            offset = midpoint + 6 * float(node)
            noise = offset - half_separation
            tail = _normal_tail(offset + half_separation)
            error = -expm1((order - 1) * log1p(-tail)) if tail < 1 else 1.0
            integral += float(weight) * exp(-0.5 * noise * noise) * error
    return 6 * integral / sqrt(2 * pi)


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
