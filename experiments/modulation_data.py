"""Genera las tablas y figuras de los apartados D y E del TP."""

import argparse
from pathlib import Path

import numpy as np

from channel.channel import channel_effects
from common.constellations import build_constellation
from common.data_types import ErrorRates
from common.file_utils import read_file
from common.modulation_metrics import (
    estimate_bit_error_rate, estimate_energies, estimate_symbol_error_rate,
    symbol_statistics, theoretical_energies, theoretical_error_rates,
)
from common.modulation_plots import plot_constellation, plot_symbol_histogram
from common.modulation_report import format_modulation_report
from config import ModulationConfig, load_channel_config
from receiver.demodulation import demodulation
from transmitter.huffman import build_huffman_code
from transmitter.modulation import modulation
from transmitter.source_analysis import analyze_source
from transmitter.source_encoder import encode_source


def generate_modulation_data(input_file: Path, output_file: Path, tipo: str, order: int) -> None:
    """Escribe un Markdown y tres PNG para una corrida reproducible a 6 dB."""
    eb_n0_db = 6.0
    seed = 42
    config = ModulationConfig(order, tipo)
    constellation = build_constellation(config)
    constellation_file = output_file.with_suffix(".constellation.png")
    histogram_file = output_file.with_suffix(".histogram.png")
    received_file = output_file.with_suffix(".received.png")
    outputs = (output_file, constellation_file, histogram_file, received_file)
    if input_file.resolve() in {path.resolve() for path in outputs}:
        raise ValueError("La entrada debe ser distinta de los archivos de salida.")

    text = read_file(input_file)
    if not text:
        raise ValueError("El archivo de entrada está vacío.")
    huffman = build_huffman_code(analyze_source(text).probabilities)
    encoded = encode_source(text, huffman.codebook)
    if len(encoded.bits) < 4:
        raise ValueError("Se requieren al menos cuatro bits para cubrir M = 16.")

    transmitted = modulation(encoded, config)
    histogram = symbol_statistics(transmitted, constellation)
    rng = np.random.default_rng(seed)
    channel = load_channel_config(eb_n0_db, config.Eb)
    noisy = channel_effects(transmitted, config, channel, rng=rng)
    decided = demodulation(noisy, config)
    measured_ber = estimate_bit_error_rate(encoded.bits, decided.bits)
    measured_ser = estimate_symbol_error_rate(transmitted.symbols, decided.symbols)
    selected_report = format_modulation_report(
        config, theoretical_energies(config), estimate_energies(transmitted.symbols, config),
        theoretical_error_rates(config, eb_n0_db), ErrorRates(measured_ser, measured_ber.error_rate),
        histogram,
    )

    lines = [
        "# Datos para el informe de modulación y canal",
        "",
        f"- Entrada: `{input_file}` ({len(text)} caracteres).",
        f"- Bits codificados con Huffman: {len(encoded.bits)}.",
        f"- Configuración de los gráficos y la corrida con ruido: {order}-{tipo} Gray.",
        "- Energía nominal de bit Eb = 1 en unidades normalizadas y tasa de código = 1.",
        "",
        "## D. Energías y probabilidades por esquema y orden",
        "",
        "Las energías estimadas se calcularon sobre los símbolos transmitidos del texto indicado.",
        "Las probabilidades teóricas corresponden a AWGN a 6 dB, con símbolos equiprobables.",
        "",
        "| Esquema | M | Es teórica | Eb teórica | Es estimada | Eb estimada | SER teórica | BER Gray | BER binaria |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for scheme in ("PAM", "FSK"):
        for size in (2, 4, 8, 16):
            row_config = ModulationConfig(size, scheme)
            symbols = transmitted.symbols if row_config == config else modulation(encoded, row_config).symbols
            theoretical = theoretical_energies(row_config)
            estimated = estimate_energies(symbols, row_config)
            gray = theoretical_error_rates(row_config, eb_n0_db)
            binary = theoretical_error_rates(ModulationConfig(size, scheme, labeling="binary"), eb_n0_db)
            lines.append(
                f"| {scheme} | {size} | {theoretical.symbol_energy:.9g} | {theoretical.bit_energy:.9g} | "
                f"{estimated.symbol_energy:.9g} | {estimated.bit_energy:.9g} | {gray.symbol_error_rate:.9g} | "
                f"{gray.bit_error_rate:.9g} | {binary.bit_error_rate:.9g} |"
            )

    sample_size = min(len(noisy.symbols), 400)
    sample_indices = rng.choice(len(noisy.symbols), size=sample_size, replace=False)
    lines += [
        "",
        "## D. Constelación e histograma del transmisor",
        "",
        f"![Constelación transmitida de {order}-{tipo}]({constellation_file.name})",
        "",
        f"![Conteos y frecuencias de los símbolos transmitidos]({histogram_file.name})",
        "",
        "Los conteos de la tabla siguiente usan todos los símbolos transmitidos.",
        f"La frecuencia de referencia equiprobable es 1/M = {1 / order:.9g}.",
        "La tabla de errores para esta configuración usa la corrida con AWGN descrita en E.",
        "",
        selected_report.rstrip(),
        "",
        "## E. Muestras a la entrada del receptor",
        "",
        f"- Canal AWGN a {eb_n0_db:g} dB. Semilla del generador: {seed}.",
        f"- N0 = {channel.N0:.9g}. Varianza del ruido por coordenada: {channel.N0 / 2:.9g}.",
        f"- Símbolos transmitidos y evaluados para la SER: {len(transmitted.symbols)}.",
        f"- Bits recuperados tras demodular: {len(decided.bits)}.",
        f"- Bits descartados al modular: {len(encoded.bits) - len(decided.bits)}.",
        f"- Bits errados para la BER: {measured_ber.bits_errados} de {measured_ber.bits_vistos}.",
        f"- La figura muestra {sample_size} muestras recibidas, seleccionadas de la corrida completa.",
        "",
        f"![Constelación recibida de {order}-{tipo} con AWGN a 6 dB]({received_file.name})",
    ]

    output_file.parent.mkdir(parents=True, exist_ok=True)
    plot_constellation(constellation, constellation_file)
    plot_symbol_histogram(histogram, histogram_file)
    plot_constellation(constellation, received_file, received_symbols=noisy.symbols[sample_indices])
    output_file.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("res/textito.txt"))
    parser.add_argument("--output", type=Path, default=Path("res/modulation_info.md"))
    parser.add_argument("--tipo", choices=("PAM", "FSK"), default="PAM")
    parser.add_argument("--orden", type=int, choices=(2, 4, 8, 16), default=4)
    args = parser.parse_args()
    generate_modulation_data(args.input, args.output, args.tipo, args.orden)
