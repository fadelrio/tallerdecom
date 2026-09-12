"""Orquestador conceptual de los apartados A/B, sin invocar algoritmos."""

from config import load_config


def main() -> None:
    """Carga la configuración y muestra el flujo y sus etapas pendientes.

    Notes:
        Solo la configuración y la visualización de estados están operativas.
        No invoca placeholders ni fabrica resultados intermedios. Las
        interfaces se conectarán cuando sus funcionalidades se implementen.
    """
    print("=" * 60)
    print(" SISTEMA DE COMUNICACIONES DIGITALES")
    print("=" * 60)
    print("\n[CONFIG] Cargando configuración...")
    config = load_config()
    print(f"[FILE] Archivo de entrada: {config.input_file}")
    print(f"[FILE] Archivo de salida: {config.output_file}")
    print("[FILE] Lectura binaria                         [PENDIENTE]")
    print("\n[TRANSMISOR]")
    print("[SOURCE] Análisis estadístico y entropía        [PENDIENTE]")
    print("[SOURCE] Construcción del código Huffman        [PENDIENTE]")
    print("[SOURCE] Estadísticas del código y eficiencia   [PENDIENTE]")
    print("[SOURCE] Codificación de fuente                 [PENDIENTE]")
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
