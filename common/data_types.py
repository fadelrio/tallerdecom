"""Estructuras compartidas; no realizan cálculos ni validaciones."""

from dataclasses import dataclass


@dataclass
class SourceStatistics:
    """Resultados del análisis de una fuente de bytes.

    Attributes:
        counts: Cantidad de apariciones por símbolo entero entre 0 y 255.
        probabilities: Probabilidad por símbolo entero entre 0 y 255.
        total_symbols: Cantidad total de bytes de la fuente.
        entropy: Entropía de la fuente en bits por símbolo.
    """

    counts: dict[int, int]
    probabilities: dict[int, float]
    total_symbols: int
    entropy: float


@dataclass
class CodeStatistics:
    """Características de las palabras del código Huffman.

    Attributes:
        minimum_length: Longitud mínima de una palabra en bits.
        average_length: Longitud promedio ponderada en bits por símbolo.
        variance: Varianza de las longitudes ponderada por probabilidad,
            en bits cuadrados.
        is_prefix_code: Indica si ninguna palabra es prefijo de otra.
    """

    minimum_length: int
    average_length: float
    variance: float
    is_prefix_code: bool


@dataclass
class HuffmanResult:
    """Código Huffman y sus estadísticas.

    Attributes:
        codebook: Palabra binaria de cada símbolo entero entre 0 y 255.
        statistics: Características del código construido.
    """

    codebook: dict[int, str]
    statistics: CodeStatistics


@dataclass
class EncodedSource:
    """Representación inicial de la fuente codificada.

    Attributes:
        bits: Secuencia binaria representada por caracteres '0' y '1'.
    """

    bits: str


@dataclass
class FileComparison:
    """Resultado de comparar la fuente original y la recibida.

    Attributes:
        identical: Indica igualdad exacta de ambas secuencias de bytes.
        original_size: Tamaño original en bytes.
        received_size: Tamaño recibido en bytes.
    """

    identical: bool
    original_size: int
    received_size: int


@dataclass
class SourceReport:
    """Fila de la tabla de símbolos del informe B.

    Attributes:
        symbol: Byte de la fuente como entero entre 0 y 255.
        count: Cantidad de apariciones del símbolo.
        probability: Probabilidad del símbolo.
        huffman_code: Palabra binaria asignada al símbolo.
    """

    symbol: int
    count: int
    probability: float
    huffman_code: str


@dataclass
class CodingReport:
    """Resultados necesarios para comparar Huffman con un código fijo.

    Attributes:
        entropy: Entropía en bits por símbolo.
        minimum_length: Longitud mínima de Huffman en bits.
        average_length: Longitud promedio de Huffman en bits por símbolo.
        variance: Varianza de longitudes en bits cuadrados.
        efficiency: Cociente adimensional entre entropía y longitud promedio.
        fixed_code_length: Longitud fija de referencia: 8 bits por símbolo.
        huffman_total_bits: Cantidad de bits de la secuencia codificada.
        fixed_total_bits: Cantidad de símbolos multiplicada por 8 bits.
    """

    entropy: float
    minimum_length: int
    average_length: float
    variance: float
    efficiency: float
    fixed_code_length: int
    huffman_total_bits: int
    fixed_total_bits: int
