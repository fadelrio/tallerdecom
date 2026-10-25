"""Presentación del informe de modulación, sin cálculos ni conclusiones."""

from html import escape

from common.data_types import EnergyStatistics, ErrorRates, SymbolStatistics
from config import ModulationConfig, validate_modulation_config


def format_modulation_report(
    config: ModulationConfig,
    theoretical_energies: EnergyStatistics,
    estimated_energies: EnergyStatistics,
    theoretical_errors: ErrorRates,
    estimated_errors: ErrorRates,
    statistics: SymbolStatistics,
) -> str:
    """Ordena los resultados recibidos de una configuración en Markdown.

    Args:
        config: Esquema, M, etiquetas y tasa de código utilizados.
        theoretical_energies: Referencias de Es, Ec y Eb ya calculadas.
        estimated_energies: Energías medidas en la secuencia transmitida.
        theoretical_errors: Referencias teóricas de SER y BER en AWGN.
        estimated_errors: SER y BER medidas en la simulación.
        statistics: Conteos y probabilidades por etiqueta de modulación.

    Returns:
        Markdown con identificación de PAM/FSK, M y etiquetamiento, tablas de
        energías teóricas/estimadas, errores teóricos/estimados e histograma.

    Raises:
        ValueError: Si la configuración es inválida o las etiquetas, conteos
            y probabilidades tienen longitudes diferentes.

    Notes:
        No calcula métricas ni genera gráficos o archivos. Los errores
        teóricos son referencias en AWGN; el llamador debe indicar su Eb/N0
        y las condiciones de la simulación para evitar comparaciones ambiguas.
        Las hipótesis teóricas y la interpretación del histograma y de Gray
        deben explicarse en el informe elaborado por los estudiantes.
    """
    validate_modulation_config(config)
    lines = [
        "## DATOS DE MODULACIÓN Y DEMODULACIÓN",
        "",
        f"- Esquema: {config.tipo}",
        f"- Orden M: {config.M}",
        f"- Etiquetamiento: {config.labeling}",
        f"- Energía nominal Eb de información: {config.Eb:.12g}",
        f"- Tasa de código k/n: {config.code_rate:.12g}",
        "",
        "### 1. ENERGÍAS MEDIAS",
        "",
        "| Magnitud | Teórica | Estimada |",
        "| --- | ---: | ---: |",
        f"| Es (símbolo de modulación) | {theoretical_energies.symbol_energy:.12g} | {estimated_energies.symbol_energy:.12g} |",
        f"| Ec (bit de canal) | {theoretical_energies.channel_bit_energy:.12g} | {estimated_energies.channel_bit_energy:.12g} |",
        f"| Eb (bit de información) | {theoretical_energies.bit_energy:.12g} | {estimated_energies.bit_energy:.12g} |",
        "",
        "Energías expresadas en unidades normalizadas.",
        "",
        "### 2. PROBABILIDADES DE ERROR",
        "",
        "| Magnitud | Referencia teórica (AWGN) | Estimada (simulación) |",
        "| --- | ---: | ---: |",
        f"| SER | {theoretical_errors.symbol_error_rate:.12g} | {estimated_errors.symbol_error_rate:.12g} |",
        f"| BER | {theoretical_errors.bit_error_rate:.12g} | {estimated_errors.bit_error_rate:.12g} |",
        "",
        "Las probabilidades son adimensionales. La referencia teórica supone",
        "símbolos equiprobables y recepción coherente, antes de decodificar el canal.",
        "",
        "### 3. OCURRENCIA DE SÍMBOLOS MODULADOS",
        "",
        "| Etiqueta | Cantidad | Probabilidad observada |",
        "| --- | ---: | ---: |",
    ]
    for label, count, probability in zip(
        statistics.labels, statistics.counts, statistics.probabilities, strict=True,
    ):
        cell = escape(label, quote=False)
        for character, entity in (("|", "&#124;"), ("`", "&#96;"),
                                  ("\n", "&#10;"), ("\r", "&#13;")):
            cell = cell.replace(character, entity)
        lines.append(f"| {cell} | {count:d} | {probability:.12g} |")
    return "\n".join(lines) + "\n"
