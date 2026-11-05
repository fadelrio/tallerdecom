"""

IMPORTANTE: CORRER CON ESTE COMANDO: python -m experiments.experimento_PAM

"""

from channel.channel import channel_effects
from common.data_types import EncodedSource
from common.file_utils import compare_data, read_file, write_file
from common.modulation_metrics import estimate_bit_error_rate, estimate_energies
from common.report_utils import format_source_report
from config import SimulationConfig, load_channel_config, load_config, load_modulation_config

from html import escape

from receiver.demodulation import demodulation
from receiver.source_decoder import decode_source

from transmitter.huffman import build_huffman_code
from transmitter.source_analysis import analyze_source
from transmitter.source_encoder import encode_source
from transmitter.modulation import modulation


def run_experiment(config: SimulationConfig) -> None:
    """Muestra las coordenadas de una fuente local; no escribe archivos.

    Args:
        config: Rutas del archivo de entrada UTF-8 y de salida.

    Returns:
        None; muestra las coordenadas de la fuente en la consola.

    Notes:
        Usa los cálculos existentes de fuente y modulación. El archivo de salida
        configurado no se escribe desde este experimento.
    """
    print("# EXPERIMENTO\n")
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
    encoded_bits_source = encode_source(data, huffman.codebook)
    
    modulacion_config = load_modulation_config(16, 'PAM', 1.0)
    datos_modulados = modulation(encoded_bits_source, modulacion_config)

    channel_config = load_channel_config(9.0, modulacion_config.Eb)
    datos_canal = channel_effects(datos_modulados, modulacion_config, channel_config)

    datos_demodulados = demodulation(datos_canal, modulacion_config)

    encoded_bits_receiver = EncodedSource(bits=datos_demodulados.bits)
    error_rate = estimate_bit_error_rate(encoded_bits_source.bits, encoded_bits_receiver.bits)
    received = decode_source(encoded_bits_receiver, huffman.codebook)

    try:
        write_file(config.output_file, received)
        saved = read_file(config.output_file)
    except (OSError, UnicodeError) as error:
        print(f"[ERROR] No se pudo escribir o releer la salida: {error}")
        return
    

if __name__ == "__main__":
    run_experiment(load_config())
