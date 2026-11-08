"""Energías y tasas de error de modulación."""

from itertools import zip_longest
from math import erfc, exp, expm1, isfinite, log, log1p, log2, pi, sqrt
from numbers import Real

import numpy as np

from common.constellations import build_constellation
from common.data_types import (
    Constellation, EnergyStatistics, ErrorRates, ModulatedData, SymbolStatistics, BitErrorRate
)
from config import ModulationConfig, validate_modulation_config


def estimate_energies(
    symbols: np.ndarray, config: ModulationConfig,
) -> EnergyStatistics:
    """Estima las energías medias de la secuencia transmitida.

    Args:
        symbols: Coordenadas reales no vacías (N, D), incluyendo el símbolo final.
        config: Orden de modulación y tasa de código compartidos.

    Returns:
        Energías medias por símbolo, bit de canal y bit de información.

    Raises:
        ValueError: Para una muestra vacía, dimensiones incompatibles o
            coordenadas inválidas.

    Notes:
        Usar la energía en una base ortonormal. No suponer equiprobabilidad en
        la muestra ni forzar el resultado al Eb nominal de la configuración.
    """

    validate_modulation_config(config)
    symbols = np.asarray(symbols)
    dimension = 1 if config.tipo == "PAM" else config.M
    if symbols.ndim != 2 or symbols.shape[0] == 0 or symbols.shape[1] != dimension:
        raise ValueError("La muestra debe ser una matriz no vacía con la dimensión del esquema.")
    if symbols.dtype.kind not in "iuf" or not np.isfinite(symbols).all():
        raise ValueError("Las coordenadas deben ser reales y finitas.")

    symbol_energy = float(np.mean(np.sum(np.square(symbols, dtype=float), axis=1)))
    channel_bit_energy = symbol_energy / log2(config.M) #CREO QUE ESTA CUENTA ESTÁ MAL
    bit_energy = symbol_energy / log2(config.M)
    return EnergyStatistics(symbol_energy, channel_bit_energy, bit_energy)


def theoretical_energies(config: ModulationConfig) -> EnergyStatistics:
    """Calcula la referencia energética para símbolos equiprobables.

    Args:
        config: Orden, energía de información y tasa de código.

    Returns:
        Energías teóricas por símbolo, bit de canal y bit de información.

    Raises:
        ValueError: Para una configuración inválida.

    Notes:
        Diferenciar Eb de información y Ec del flujo de canal. Una muestra
        PAM no equiprobable puede diferir de esta referencia.
    """
    validate_modulation_config(config)
    channel_bit_energy = float(config.Eb * config.code_rate)
    return EnergyStatistics(channel_bit_energy * log2(config.M), channel_bit_energy, float(config.Eb))

    
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
    """Compara las secuencias binarias transmitida y recibida.

    Args:
        transmitted: Bits originales, sin relleno de modulación.
        received: Bits recibidos.

    Returns:
        Tasa de error, cantidad de posiciones evaluadas y cantidad de errores.

    Raises:
        ValueError: Si alguna secuencia está vacía o contiene caracteres
            distintos de '0' y '1'.

    Notes:
        Compara flujos de la misma etapa, antes de decodificar Huffman.
        Cada bit sin contraparte cuenta como error. La longitud de la secuencia
        más larga es el denominador.
    """
    # Validar que las secuencias no estén vacías.
    if not transmitted or not received:
        raise ValueError("Las secuencias no pueden estar vacías.")

    # Validar que las secuencias contengan solo '0' y '1'.
    if not all(bit in '01' for bit in transmitted):
        raise ValueError("La secuencia transmitida contiene caracteres inválidos.")

    if not all(bit in '01' for bit in received):
        raise ValueError("La secuencia recibida contiene caracteres inválidos.")

    # Contar bits distintos.
    differing_bits = sum(
        t_bit != r_bit
        for t_bit, r_bit in zip_longest(transmitted, received, fillvalue=None)
    )
    total_bits = max(len(transmitted), len(received))
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
    """Calcula los conteos y frecuencias de los símbolos transmitidos.

    Args:
        modulated: Símbolos transmitidos (N, D), incluyendo el símbolo final.
        constellation: Todas las coordenadas y etiquetas posibles.

    Returns:
        Etiquetas, conteos y frecuencias en el orden de la constelación,
        incluyendo ceros para símbolos no observados.

    Raises:
        ValueError: Para una muestra vacía, una constelación incompatible
            o símbolos ajenos a ella.

    Notes:
        No asumir equiprobabilidad ni emitir conclusiones sobre el histograma.
    """
    samples = np.asarray(modulated.symbols)
    points = np.asarray(constellation.symbols)
    if (
        samples.ndim != 2 or samples.size == 0 or points.ndim != 2
        or points.size == 0 or points.shape[1] != samples.shape[1]
        or len(points) != len(constellation.labels)
    ):
        raise ValueError("La muestra y la constelación deben ser matrices compatibles y no vacías.")
    if points.dtype.kind not in "iuf" or not np.isfinite(points).all():
        raise ValueError("Las coordenadas de la constelación deben ser reales y finitas.")
    if samples.dtype.kind not in "iuf" or not np.isfinite(samples).all():
        raise ValueError("Las coordenadas de la muestra deben ser reales y finitas.")

    point_indices = {tuple(point): index for index, point in enumerate(points)}
    if len(point_indices) != len(points) or len(set(constellation.labels)) != len(points):
        raise ValueError("La constelación debe tener coordenadas y etiquetas únicas.")

    counts = np.zeros(len(points), dtype=int)
    try:
        for sample in samples:
            counts[point_indices[tuple(sample)]] += 1
    except KeyError as error:
        raise ValueError("La muestra contiene un símbolo ajeno a la constelación.") from error
    return SymbolStatistics(list(constellation.labels), counts, counts / len(samples))
