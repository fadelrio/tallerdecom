"""Flujo directo de fuente y datos del apartado B."""

from common.file_utils import compare_data, read_file, write_file
from common.report_utils import format_source_report
from config import SimulationConfig, load_config
from pathlib import Path
import argparse
from html import escape
from receiver.source_decoder import decode_source
from transmitter.huffman import build_huffman_code
from transmitter.source_analysis import analyze_source
from transmitter.source_encoder import encode_source


def main() -> None:
    """Ejecuta archivo → Huffman → decodificación → archivo e imprime datos.

    Notes:
        Usa las rutas de load_config. Controla errores de E/S y entrada vacía.
        La salida del codificador entra directamente al decodificador.
        Relee la salida escrita antes de compararla con el original.
    """
    run_simulation(load_config())


def run_simulation(config: SimulationConfig) -> None:
    """Procesa un TXT local propio o descargado, sin alterar su contenido.

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
    encoded = encode_source(data, huffman.codebook)
    print(f"Fuente codificada: {len(encoded.bits)} bits\n")
    # Conexión directa: no hay operaciones de canal entre ambos bloques.
    received = decode_source(encoded, huffman.codebook)
    try:
        write_file(config.output_file, received)
        saved = read_file(config.output_file)
    except (OSError, UnicodeError) as error:
        print(f"[ERROR] No se pudo escribir o releer la salida: {error}")
        return
    comparison = compare_data(data, saved)
    print(format_source_report(
        data, saved, statistics, huffman, encoded, comparison,
    ))


def cli() -> None:
    """Selecciona archivos desde la terminal y ejecuta la simulación.

    Notes:
        Sin argumentos se usan las rutas de config.py. Los archivos de
        Gutenberg deben estar descargados en formato texto UTF-8.
    """
    defaults = load_config()
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
