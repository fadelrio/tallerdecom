"""

IMPORTANTE: CORRER CON ESTE COMANDO: python -m experiments.energias_estimadas

Experimento: a partir del texto, generar los símbolos modulados y estimar sus energías con la función
estimate_energies().

"""

from common.file_utils import read_file
from common.modulation_metrics import estimate_energies
from config import SimulationConfig, load_config, load_modulation_config

from html import escape

from transmitter.huffman import build_huffman_code
from transmitter.source_analysis import analyze_source
from transmitter.source_encoder import encode_source
from transmitter.modulation import modulation


def run_experiment(config: SimulationConfig) -> None:
    """Muestra las energías estimadas de una fuente local; no escribe archivos.
    Muestra las energías estimadas para PAM y FSK, con M potencia de 2 entre 2 y 16, y Eb = 1.0.
    Debe iterar en un ciclo for sobre todas las combinaciones de M y tipo de modulación, y 
    mostrar los resultados en la consola.
    Args:
        config: Rutas del archivo de entrada UTF-8 y de salida.

    Returns:
        None; muestra las energías estimadas en la consola.
    
    """

    print("# EXPERIMENTO ENERGÍAS ESTIMADAS\n")
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

    for tipo in ("PAM", "FSK"):
        for M in (2, 4, 8, 16):
            modulation_config = load_modulation_config(M, tipo, 1.0)
            modulated = modulation(encoded_bits_source, modulation_config)
            if modulated.symbols.size == 0:
                print(
                    f"- {tipo}, M={M}: no se pudo estimar la energía; "
                    "la fuente no contiene bits suficientes para formar un símbolo."
                )
                continue

            energies = estimate_energies(modulated.symbols, modulation_config)
            print(
                f"- {tipo}, M={M}: "
                f"Es={energies.symbol_energy:.12g}, "
                f"Eb={energies.bit_energy:.12g}"
            )


if __name__ == "__main__":
    run_experiment(load_config())
    