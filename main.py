"""Orquestación del transmisor y presentación de las etapas pendientes."""

from config import load_config
from common.file_utils import read_file
from transmitter.source_analysis import analyze_source
from transmitter.huffman import build_huffman_code, calculate_efficiency
from transmitter.source_encoder import encode_source


def main() -> None:
    """Carga la fuente y ejecuta el transmisor cuando hay un archivo válido.

    Notes:
        Rechaza archivos vacíos antes de Huffman y controla errores de E/S.
        Si el archivo no existe, muestra el recorrido conceptual.
        No invoca el receptor ni las otras interfaces pendientes.
    """
    print("=" * 60)
    print(" SISTEMA DE COMUNICACIONES DIGITALES")
    print("=" * 60)
    print("\n[CONFIG] Cargando configuración...")
    config = load_config()
    print(f"[FILE] Archivo de entrada: {config.input_file}")
    print(f"[FILE] Archivo de salida: {config.output_file}")
    # Sin archivo se conserva el recorrido conceptual del proyecto.
    try:
        data = read_file(config.input_file)
    except FileNotFoundError:
        print("[FILE] Archivo no encontrado; recorrido conceptual.")
        data = None
    except OSError as error:
        print(f"[ERROR] No se pudo leer el archivo: {error}")
        return

    # Rechazamos el vacío antes de construir Huffman. No se genera salida
    # ni se presenta como exitosa una transmisión que no se realizó.
    if data == b"":
        print("[ERROR] Archivo vacío: se requiere al menos un byte.")
        return

    if data is not None:
        statistics = analyze_source(data)
        huffman = build_huffman_code(statistics.probabilities)
        efficiency = calculate_efficiency(
            statistics.entropy, huffman.statistics.average_length
        )
        encoded = encode_source(data, huffman.codebook)
        print(f"[SOURCE] Fuente codificada: {len(encoded.bits)} bits.")
        print(f"[SOURCE] Eficiencia: {efficiency:.4f}")
    print("\n[TRANSMISOR]")
    print("[SOURCE] Análisis estadístico y entropía        [DISPONIBLE]")
    print("[SOURCE] Construcción del código Huffman        [DISPONIBLE]")
    print("[SOURCE] Estadísticas del código y eficiencia   [DISPONIBLE]")
    print(
        "[SOURCE] Codificación por bloques               [DISPONIBLE]"
    )
    print("[CHANNEL] Codificación de canal                 [NO IMPLEMENTADO]")
    print("[CHANNEL] Modulación                            [NO IMPLEMENTADO]")
    print("\n[CANAL]")
    print("[CHANNEL] AWGN                                  [NO IMPLEMENTADO]")
    print("[CHANNEL] Respuesta impulsiva                   [NO IMPLEMENTADO]")
    print("\n[RECEPTOR]")
    print("[CHANNEL] Demodulación                          [NO IMPLEMENTADO]")
    print("[CHANNEL] Decodificación de canal               [NO IMPLEMENTADO]")
    print("[SOURCE] Decodificación de fuente               [PENDIENTE]")
    print("\n[RESULTADO]")
    print("[FILE] Escritura del archivo recibido          [PENDIENTE]")
    print("[FILE] Comparación con el original             [PENDIENTE]")
    print("[REPORT] Tabla de símbolos y métricas           [PENDIENTE]")
    print("\n[PENDIENTE]: funcionalidad de A/B aún sin implementar.")
    print("[NO IMPLEMENTADO]: etapa futura de la consigna.")


if __name__ == "__main__":
    main()
