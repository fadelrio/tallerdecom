"""

IMPORTANTE: CORRER CON ESTE COMANDO: python -m experiments.experimento_PAM

"""

from common.file_utils import compare_data, read_file, write_file
from common.report_utils import format_source_report
from config import SimulationConfig, load_config, load_modulation_config
from pathlib import Path
import argparse
from html import escape
from main import run_simulation
from receiver.source_decoder import decode_source
from transmitter.huffman import build_huffman_code
from transmitter.source_analysis import analyze_source
from transmitter.source_encoder import encode_source
from transmitter.modulation import modulation

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
    
    modulacion_config = load_modulation_config(16, 'PAM', 1.0)
    datos_modulados = modulation(encoded, modulacion_config)

    print(f"Cantidad original de bits: {len(encoded.bits)}\n\n")
    print("\n################################\n")
    print(f"bits de padding agregados: {datos_modulados.padding_bits}\n")
    print("\n################################\n")
    print(f"Dimensión de los datos modulados: {datos_modulados.symbols.shape}\n")
    print("\n################################\n")
    print(f"Primeros 10 datos modulados:\n{datos_modulados.symbols[:10]}\n")