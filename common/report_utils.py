"""Preparación y presentación de datos del apartado B, sin conclusiones."""

from html import escape
import re

from transmitter.huffman import calculate_efficiency
from receiver.source_decoder import decode_source
from transmitter.source_encoder import encode_source

from common.data_types import (
    CodingReport,
    FileComparison,
    EncodedSource,
    HuffmanResult,
    SourceReport,
    SourceStatistics,
)


def _fits_fixed_code(symbol: str) -> bool:
    """Comprueba la codificación real, sin descartar ni sustituir caracteres."""
    try:
        symbol.encode("cp1252", errors="strict")
    except UnicodeEncodeError:
        return False
    return True


def build_source_table(
    statistics: SourceStatistics,
    huffman: HuffmanResult,
) -> list[SourceReport]:
    """Prepara la tabla de símbolos del informe B.

    Args:
        statistics: Conteos y probabilidades de la fuente.
        huffman: Código Huffman de los símbolos observados.

    Returns:
        Una fila por símbolo con su carácter Unicode, cantidad, probabilidad
        y palabra Huffman.

    Notes:
        La representación legible de caracteres de control corresponde a una
        futura capa de presentación; no modifica los símbolos internos.
    """
    return [
        SourceReport(symbol, statistics.counts[symbol],
                     statistics.probabilities[symbol], huffman.codebook[symbol])
        for symbol in sorted(statistics.counts)
    ]


def build_coding_report(
    statistics: SourceStatistics,
    huffman: HuffmanResult,
    encoded: EncodedSource,
) -> CodingReport:
    """Prepara las métricas comparativas del informe B.

    Args:
        statistics: Entropía y cantidad total de símbolos de la fuente.
        huffman: Código y estadísticas de sus longitudes.
        encoded: Secuencia codificada cuya longitud dará el total de bits.

    Returns:
        Entropía, longitud mínima y promedio, varianza, eficiencia como
        fracción, longitud fija de 8 bits y totales de bits Huffman y fijo.

    Notes:
        La referencia es Windows-1252 (cp1252), de 8 bits. Si un carácter no
        cabe, fixed_representable será False: el total fijo es entonces solo
        el cálculo nominal 8*N, no una codificación realizable en esa tabla.
        No genera PDF ni Word.
    """
    representable = all(_fits_fixed_code(symbol) for symbol in statistics.counts)
    code = huffman.statistics
    return CodingReport(
        entropy=statistics.entropy,
        minimum_length=code.minimum_length,
        average_length=code.average_length,
        variance=code.variance,
        efficiency=calculate_efficiency(statistics.entropy, code.average_length),
        fixed_code_length=8,
        huffman_total_bits=len(encoded.bits),
        fixed_total_bits=8 * statistics.total_symbols,
        fixed_representable=representable,
    )

def print_source(stats: SourceStatistics) -> None:
    """Imprime conteos y probabilidades por carácter.

    Args:
        stats: Estadísticas de la fuente textual.
    """
    print("Carácter | Cantidad | Probabilidad")
    for symbol in sorted(stats.counts):
        print(f"{symbol!r} | {stats.counts[symbol]} | "
              f"{stats.probabilities[symbol]:.4f}")
    print(f"- Total de caracteres: {stats.total_symbols}")
    print(f"Entropía: {stats.entropy:.4f} bits/carácter")


def print_huffman(result: HuffmanResult) -> None:
    """Imprime palabras Huffman y métricas, escapando controles.

    Args:
        result: Código y estadísticas calculadas.
    """
    for symbol, word in sorted(result.codebook.items()):
        print(f"{symbol!r}: {word}")
    stats = result.statistics
    print(f"Largo promedio mínimo teórico: {stats.minimum_length}")
    print(f"Largo promedio: {stats.average_length}")
    print(f"Varianza: {stats.variance}")
    print(f"Código prefijo: {stats.is_prefix_code}")


def _markdown_cell(value: str) -> str:
    """Escapa texto literal para que no altere una tabla Markdown."""
    escaped = escape(value, quote=False)
    for character in "\\|`*_[]":
        escaped = escaped.replace(character, f"&#{ord(character)};")
    return escaped


def format_source_report(
    original: str,
    received: str,
    statistics: SourceStatistics,
    huffman: HuffmanResult,
    encoded: EncodedSource,
    comparison: FileComparison,
) -> str:
    """Ordena los datos del informe B en Markdown para consola o redirección.

    Args:
        original: Texto transmitido no vacío.
        received: Texto recuperado.
        statistics: Estadísticas de la fuente completa.
        huffman: Código y métricas.
        encoded: Secuencia binaria transmitida.
        comparison: Comparación con el archivo recibido releído.

    Returns:
        Markdown con tablas y muestra, sin interpretación ni conclusiones.

    Notes:
        repr permite distinguir controles y espacios. La primera línea
        conserva su terminador. Se decodifican sus bits para la muestra.
        Los totales no incluyen transporte del diccionario ni metadatos.
    """
    rows = build_source_table(statistics, huffman)
    report = build_coding_report(statistics, huffman, encoded)
    # Verificación independiente: ninguna palabra puede iniciar otra.
    words = list(huffman.codebook.values())
    prefix = all(
        not other.startswith(word)
        for i, word in enumerate(words)
        for j, other in enumerate(words) if i != j
    ) and all(words)
    lines = [
        "## DATOS DEL APARTADO B",
        "",
        "### 1. CARACTERES Y CÓDIGO HUFFMAN",
        "",
        "| Carácter (repr) | Unicode | Cantidad | Probabilidad | Código | Bits |",
        "| --- | --- | ---: | ---: | --- | ---: |",
    ]
    for row in rows:
        lines.append(
            f"| {_markdown_cell(repr(row.symbol))} | U+{ord(row.symbol):04X} | {row.count} | "
            f"{row.probability:.12g} | {row.huffman_code} | "
            f"{len(row.huffman_code)} |"
        )
    lines += [
        "",
        "### 2. PROPIEDAD DE PREFIJO Y CARACTERÍSTICAS",
        "",
        f"- Verificación por pares: {prefix}",
        f"- Indicador del constructor: {huffman.statistics.is_prefix_code}",
        "- Alfabeto de código: binario (0, 1)",
        f"- Caracteres distintos: {len(rows)}",
        f"- Total de caracteres: {statistics.total_symbols}",
        f"- Menor longitud de palabra: {min(map(len, words))} bits",
        f"- Mayor longitud de palabra: {max(map(len, words))} bits",
        "",
        "### 3. MÉTRICAS",
        "",
        "| Métrica | Valor | Unidad |",
        "| --- | ---: | --- |",
        f"| Entropía H(X) | {report.entropy:.12g} | bits/carácter |",
        f"| Mínimo promedio teórico | {report.minimum_length:.12g} | bits/carácter |",
        f"| Promedio Huffman | {report.average_length:.12g} | bits/carácter |",
        f"| Varianza | {report.variance:.12g} | bits² |",
        f"| Eficiencia | {report.efficiency:.12g} | fracción |",
        f"| Eficiencia | {report.efficiency * 100:.12g} | % |",
        f"| Longitud fija | {report.fixed_code_length} | bits/carácter |",
        "",
        f"- Tabla fija de referencia: {report.fixed_encoding} (Windows-1252)",
        f"- Texto representable en tabla fija: {report.fixed_representable}",
        "",
        "### 4. TOTALES DE BITS (SIN DICCIONARIO NI METADATOS)",
        "",
        "| Código | Total de bits |",
        "| --- | ---: |",
        f"| Huffman | {report.huffman_total_bits} |",
    ]
    if report.fixed_representable:
        lines.append(f"| Código fijo de 8 bits | {report.fixed_total_bits} |")
    else:
        lines.append("| Código fijo de 8 bits | No aplicable para este texto |")
        unsupported = [_markdown_cell(repr(row.symbol)) for row in rows
                       if not _fits_fixed_code(row.symbol)]
        lines.append("\nCaracteres fuera de Windows-1252: " + ", ".join(unsupported))
    sample = original.splitlines(keepends=True)[0]
    sample_encoded = encode_source(sample, huffman.codebook)
    sample_received = decode_source(sample_encoded, huffman.codebook)
    longest = max((len(run) for run in re.findall(
        r"`+", sample + sample_received + received[:len(sample)]
    )), default=0)
    fence = "`" * max(3, longest + 1)
    lines += [
        "",
        "### 5. MUESTRA: PRIMERA LÍNEA (CONTROLES ESCAPADOS)",
        "",
        fence + "text",
        f"Original: {sample!r}",
        "Palabras por carácter: " + " ".join(
            sample_encoded.iter_codewords(huffman.codebook)
        ),
        f"Binario concatenado: {sample_encoded.bits}",
        f"Decodificada: {sample_received!r}",
        f"En archivo recibido: {received[:len(sample)]!r}",
        fence,
        "",
        "### 6. COMPARACIÓN DE ARCHIVOS",
        "",
        f"- Texto idéntico: {comparison.identical}",
        f"- Caracteres originales: {comparison.original_size}",
        f"- Caracteres recibidos: {comparison.received_size}",
    ]
    return "\n".join(lines)
