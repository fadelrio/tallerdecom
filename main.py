"""Orquestación del flujo Huffman, codificación de canal y modulación."""

from common.constellations import build_constellation
from common.channel_code import build_parity_check_matrix, build_syndrome_table
from common.data_types import EncodedSource, ErrorRates
from common.file_utils import compare_data, read_file, write_file
from common.modulation_metrics import (
    estimate_bit_error_rate, estimate_energies, estimate_symbol_error_rate,
    symbol_statistics, theoretical_energies, theoretical_error_rates,
)
from common.modulation_plots import plot_constellation, plot_symbol_histogram
from common.modulation_report import format_modulation_report
from config import (
    GROUP_4_CHANNEL_CODE, ModulationConfig, SimulationConfig, load_channel_config,
    load_config, validate_modulation_config,
)
from pathlib import Path
import argparse
from html import escape
from math import isfinite
from numbers import Real
import numpy as np
from receiver.demodulation import demodulation
from receiver.channel_decoder import decode_channel
from receiver.source_decoder import decode_source
from channel.channel import channel_effects
from transmitter.channel_encoder import encode_channel
from transmitter.huffman import build_huffman_code
from transmitter.source_analysis import analyze_source
from transmitter.source_encoder import encode_source
from transmitter.modulation import modulation


CHANNEL_EB_N0_DB = 12.0
CHANNEL_NOISE_SEED = 42
CHANNEL_CODING_ENABLED = False


def _default_simulation_config() -> SimulationConfig:
    """Usa textito.txt y conserva la ruta de salida configurada."""
    config = load_config()
    return SimulationConfig(
        input_file=config.input_file.with_name("textito.txt"),
        output_file=config.output_file,
    )


def main() -> None:
    """Ejecuta fuente, canal, modulación y las etapas inversas.

    Notes:
        Usa textito.txt como entrada y output.txt como salida.
    """
    run_simulation(_default_simulation_config())


def run_simulation(config: SimulationConfig) -> None:
    """Procesa un TXT con Huffman, código de canal, 2-PAM y sus decodificadores.

    Args:
        config: Rutas del archivo de entrada UTF-8 y de salida.
    """
    print("# SISTEMA DE COMUNICACIONES — APARTADO B\n")
    print(f"- Entrada: <code>{escape(str(config.input_file))}</code>")
    print(f"- Salida: <code>{escape(str(config.output_file))}</code>\n")
    if config.input_file.resolve() == config.output_file.resolve():
        print("[ERROR] Entrada y salida deben ser archivos distintos.")
        return
    try:
        data = read_file(config.input_file)
    except (OSError, UnicodeError) as error:
        print(f"[ERROR] No se pudo leer el archivo: {error}")
        return
    if not data:
        print("[ERROR] Archivo vacío: se requiere al menos un carácter.")
        return

    statistics = analyze_source(data)
    huffman = build_huffman_code(statistics.probabilities)
    encoded_source = encode_source(data, huffman.codebook)

    channel_code = GROUP_4_CHANNEL_CODE
    if CHANNEL_CODING_ENABLED:
        parity_check_matrix = build_parity_check_matrix(channel_code)
        syndrome_table = build_syndrome_table(parity_check_matrix)
        encoded_channel = encode_channel(encoded_source, channel_code)
        source_to_modulate = EncodedSource(bits=encoded_channel.bits)
        code_rate = channel_code.k / channel_code.n
    else:
        source_to_modulate = encoded_source
        code_rate = 1.0

    modulation_config = ModulationConfig(
        M=4,
        tipo="PAM",
        Eb=1.0,
        code_rate=code_rate,
    )

    modulated = modulation(
        source_to_modulate,
        modulation_config,
    )
    channel_config = load_channel_config(
        CHANNEL_EB_N0_DB,
        modulation_config.Eb,
    )
    noisy = channel_effects(
        modulated,
        modulation_config,
        channel_config,
        rng=np.random.default_rng(CHANNEL_NOISE_SEED),
    )
    demodulated = demodulation(noisy, modulation_config)
    if CHANNEL_CODING_ENABLED:
        decoded_channel = decode_channel(
            demodulated.bits,
            parity_check_matrix,
            syndrome_table,
            source_bit_length=encoded_channel.source_bit_length,
        )
        decoded_source = decoded_channel.source
    else:
        decoded_source = EncodedSource(bits=demodulated.bits)
    received = decode_source(decoded_source, huffman.codebook)

    print(f"Fuente codificada: {len(encoded_source.bits)} bits")
    if CHANNEL_CODING_ENABLED:
        print(f"Codificación de canal: {len(encoded_channel.bits)} bits")
        print(f"Bloques con errores detectados: {decoded_channel.detected_blocks}")
    else:
        print("Codificación de canal: desactivada")
    print(
        f"Modulación: {modulation_config.M}-{modulation_config.tipo}, Eb/N0 = {CHANNEL_EB_N0_DB:g} dB "
        f"(tasa de código {modulation_config.code_rate:.2f})"
    )

    try:
        write_file(config.output_file, received)
        saved = read_file(config.output_file)
    except (OSError, UnicodeError) as error:
        print(f"[ERROR] No se pudo escribir o releer la salida: {error}")
        return

    if CHANNEL_CODING_ENABLED:
        print(f"Bloques detectados: {decoded_channel.detected_blocks}")
        print(f"Bloques detectados sin corregir: {decoded_channel.uncorrected_blocks}")
    comparison = compare_data(data, saved)
    print(f"Texto idéntico: {comparison.identical}")
    print(f"Caracteres originales: {comparison.original_size}")
    print(f"Caracteres recibidos: {comparison.received_size}")


def run_modulation_simulation(
    config: SimulationConfig, modulation_config: ModulationConfig,
    *, eb_n0_db: float = 0.0,
) -> None:
    """Orquesta fuente, modulación, recepción, mediciones y presentación sin ruido.

    Args:
        config: Rutas de la fuente y del archivo recuperado.
        modulation_config: Parámetros compartidos por transmisor y receptor.
        eb_n0_db: Eb/N0 de información en dB, solo para la referencia teórica
            AWGN. No agrega ruido a la transmisión. Por defecto, 0 dB.

    Returns:
        None; presenta Markdown, guarda gráficos junto al archivo recibido y
        escribe/relee el texto recuperado. Los errores de E/S se informan.

    Raises:
        NotImplementedError: Si una dependencia sigue pendiente o el selector
            aún no aplica el etiquetamiento o la tasa de código solicitados.
        TypeError: Si los parámetros tienen tipos incompatibles.
        ValueError: Si la configuración o Eb/N0 son inválidos.

    Notes:
        La BER medida cuenta los bits descartados al modular. Las funciones
        de cálculo siguen en sus módulos. No oculta sus pendientes
        ni modifica la CLI del apartado B. No incorpora codificación de canal.
        Los gráficos se llaman <salida>.constellation.png y
        <salida>.histogram.png. El directorio de salida debe existir.
    """
    validate_modulation_config(modulation_config)
    if isinstance(eb_n0_db, bool) or not isinstance(eb_n0_db, Real):
        raise TypeError("eb_n0_db debe ser un número real.")
    if not isfinite(eb_n0_db):
        raise ValueError("eb_n0_db debe ser finito.")
    if modulation_config.labeling != "gray" or modulation_config.code_rate != 1.0:
        raise NotImplementedError(
            "El selector de modulación todavía no aplica labeling ni code_rate; "
            "usar Gray y code_rate=1.0 hasta implementar esa integración."
        )

    constellation_file = config.output_file.with_name(
        config.output_file.name + ".constellation.png"
    )
    histogram_file = config.output_file.with_name(
        config.output_file.name + ".histogram.png"
    )
    destinations = (config.output_file, constellation_file, histogram_file)
    if config.input_file.resolve() in [path.resolve() for path in destinations]:
        print("[ERROR] La entrada debe ser distinta de los archivos de salida.")
        return
    try:
        data = read_file(config.input_file)
    except (OSError, UnicodeError) as error:
        print(f"[ERROR] No se pudo leer el archivo: {error}")
        return
    if not data:
        print("[ERROR] Archivo vacío: se requiere al menos un carácter.")
        return

    source_statistics = analyze_source(data)
    huffman = build_huffman_code(source_statistics.probabilities)
    encoded = encode_source(data, huffman.codebook)
    constellation = build_constellation(modulation_config)
    transmitted = modulation(encoded, modulation_config)
    received = demodulation(transmitted, modulation_config)
    estimated_energy = estimate_energies(transmitted.symbols, modulation_config)
    reference_energy = theoretical_energies(modulation_config)
    measured_ber = estimate_bit_error_rate(encoded.bits, received.bits)
    estimated_errors = ErrorRates(
        symbol_error_rate=estimate_symbol_error_rate(
            transmitted.symbols, received.symbols,
        ),
        bit_error_rate=measured_ber.error_rate,
    )
    reference_errors = theoretical_error_rates(modulation_config, eb_n0_db)
    statistics = symbol_statistics(transmitted, constellation)
    report = format_modulation_report(
        modulation_config, reference_energy, estimated_energy,
        reference_errors, estimated_errors, statistics,
    )
    recovered = decode_source(EncodedSource(received.bits), huffman.codebook)
    try:
        plot_constellation(constellation, constellation_file)
        plot_symbol_histogram(statistics, histogram_file)
        write_file(config.output_file, recovered)
        saved = read_file(config.output_file)
    except (OSError, UnicodeError) as error:
        print(f"[ERROR] No se pudieron generar o releer las salidas: {error}")
        return
    comparison = compare_data(data, saved)
    print("# SISTEMA DE COMUNICACIONES — MODULACIÓN Y DEMODULACIÓN\n")
    print(f"- Entrada: <code>{escape(str(config.input_file))}</code>")
    print(f"- Salida: <code>{escape(str(config.output_file))}</code>")
    print("- Transmisión simulada: sin ruido.")
    print(f"- Referencia teórica AWGN: Eb/N0 = {eb_n0_db:.12g} dB.")
    print(f"- Bits antes de modular: {len(encoded.bits)}")
    print(f"- Se descartaron bits al modular: {'sí' if transmitted.flag_descarte else 'no'}")
    print(f"- Bits errados: {measured_ber.bits_errados} de {measured_ber.bits_vistos}\n")
    print(report)
    print(f"- Constelación: <code>{escape(str(constellation_file))}</code>")
    print(f"- Histograma: <code>{escape(str(histogram_file))}</code>")
    print(f"- Texto idéntico: {comparison.identical}")
    print(f"- Caracteres originales: {comparison.original_size}")
    print(f"- Caracteres recibidos: {comparison.received_size}")


def cli() -> None:
    """Selecciona archivos desde la terminal y ejecuta la simulación.

    Notes:
        Sin argumentos usa textito.txt y output.txt junto a las rutas de
        config.py. --input acepta archivos UTF-8 locales.
    """
    defaults = _default_simulation_config()
    parser = argparse.ArgumentParser(
        description="Simulación de fuente con TXT propios o de Gutenberg.",
    )
    parser.add_argument(
        "--input", type=Path, default=defaults.input_file,
        help="TXT UTF-8 local, propio o descargado de Gutenberg",
    )
    parser.add_argument(
        "--output", type=Path, default=defaults.output_file,
        help="Archivo recibido (se sobrescribe si existe)",
    )
    args = parser.parse_args()
    run_simulation(SimulationConfig(args.input, args.output))


if __name__ == "__main__":
    cli()
