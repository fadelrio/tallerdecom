"""Contratos para preparar datos del informe sin generar documentos."""

from common.data_types import (
    CodingReport,
    EncodedSource,
    HuffmanResult,
    SourceReport,
    SourceStatistics,
)


def build_source_table(
    statistics: SourceStatistics,
    huffman: HuffmanResult,
) -> list[SourceReport]:
    """Preparará la tabla de símbolos del informe B.

    Args:
        statistics: Conteos y probabilidades de la fuente.
        huffman: Código Huffman de los símbolos observados.

    Returns:
        Una fila por símbolo con su entero 0..255, cantidad, probabilidad
        y palabra Huffman.

    Raises:
        NotImplementedError: La preparación de la tabla está pendiente.

    Notes:
        La representación legible de bytes de control corresponde a una
        futura capa de presentación; no modifica los símbolos internos.
    """
    raise NotImplementedError("Tabla de símbolos pendiente.")


def build_coding_report(
    statistics: SourceStatistics,
    huffman: HuffmanResult,
    encoded: EncodedSource,
) -> CodingReport:
    """Preparará las métricas comparativas del informe B.

    Args:
        statistics: Entropía y cantidad total de símbolos de la fuente.
        huffman: Código y estadísticas de sus longitudes.
        encoded: Secuencia codificada cuya longitud dará el total de bits.

    Returns:
        Entropía, longitud mínima y promedio, varianza, eficiencia como
        fracción, longitud fija de 8 bits y totales de bits Huffman y fijo.

    Raises:
        NotImplementedError: La preparación del informe está pendiente.

    Notes:
        Deberá utilizar calculate_efficiency para la eficiencia. El total
        fijo será 8 por la cantidad de símbolos; el total Huffman será la
        longitud de encoded.bits. No generará PDF, Word ni otros documentos.
    """
    raise NotImplementedError("Datos comparativos del informe pendientes.")

def print_source(stats) -> None:
    """Imprime de forma legible las estadísticas de una fuente analizada.

    Args:
        stats: Resultado de analyze_source (SourceStatistics), con conteos,
            probabilidades, total de símbolos y entropía.

    Notes:
        Cada símbolo es un byte (entero 0-255), como define el contrato de
        analyze_source. Se interpreta como carácter ASCII/UTF-8 cuando es
        imprimible; los caracteres de control reciben un nombre legible
        (ESPACIO, SALTO DE LÍNEA, etc.) y los bytes fuera del rango ASCII
        imprimible se muestran en hexadecimal, porque un byte suelto puede
        ser parte de una secuencia UTF-8 multibyte y no representar un
        carácter completo por sí solo.
    """
    control_names = {
        0: "NULO",
        9: "TAB",
        10: "SALTO DE LÍNEA (\\n)",
        13: "RETORNO DE CARRO (\\r)",
        27: "ESC",
        32: "ESPACIO",
    }

    print(f"{'Símbolo':<8}{'Carácter':<24}{'Cantidad':<10}{'Probabilidad':<14}")
    print("-" * 56)

    for symbol in sorted(stats.counts):
        count = stats.counts[symbol]
        probability = stats.probabilities[symbol]

        if symbol in control_names:
            char_repr = control_names[symbol]
        elif 33 <= symbol <= 126:
            char_repr = f"'{chr(symbol)}'"
        else:
            char_repr = f"\\x{symbol:02x}"

        print(f"{symbol:<8}{char_repr:<24}{count:<10}{probability:<14.4f}")

    print("-" * 56)
    print(f"Total de símbolos: {stats.total_symbols}")
    print(f"Entropía: {stats.entropy:.4f} bits/símbolo")

def print_huffman(result) -> None:
    """Imprime de forma legible el código Huffman y sus estadísticas.

    Args:
        result: HuffmanResult devuelto por build_huffman_code: contiene
            el codebook (símbolo -> palabra binaria) y sus CodeStatistics
            (longitud mínima, promedio, varianza, propiedad de prefijo).

    Notes:
        Cada símbolo es un byte (entero 0-255), consistente con el criterio
        de print_source: no se intenta reconstruir caracteres especiales
        a partir de bytes UTF-8 combinados, cada byte se muestra como su
        propio símbolo.

        Ordena los símbolos por longitud de palabra (más cortas primero)
        y, dentro de la misma longitud, por símbolo. Así se ve de un
        vistazo el principio central de Huffman: los símbolos más
        frecuentes deberían tener las palabras más cortas.
    """
    control_names = {
        0: "NULO",
        9: "TAB",
        10: "SALTO DE LÍNEA (\\n)",
        13: "RETORNO DE CARRO (\\r)",
        27: "ESC",
        32: "ESPACIO",
    }

    codebook = result.codebook
    stats = result.statistics

    print(f"{'Símbolo':<8}{'Carácter':<24}{'Código':<14}{'Long.':<6}")
    print("-" * 52)

    for symbol in sorted(codebook, key=lambda s: (len(codebook[s]), s)):
        code = codebook[symbol]

        if symbol in control_names:
            char_repr = control_names[symbol]
        elif 33 <= symbol <= 126:
            char_repr = f"'{chr(symbol)}'"
        else:
            char_repr = f"\\x{symbol:02x}"

        print(f"{symbol:<8}{char_repr:<24}{code:<14}{len(code):<6}")

    print("-" * 52)
    print(f"Longitud mínima: {stats.minimum_length} bits")
    print(f"Longitud promedio: {stats.average_length:.4f} bits/símbolo")
    print(f"Varianza: {stats.variance:.4f} bits²")
    print(f"¿Es código prefijo?: {'Sí' if stats.is_prefix_code else 'No'}")