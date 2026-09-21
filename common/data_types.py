"""Estructuras compartidas; no realizan cálculos ni validaciones."""

from dataclasses import dataclass
from collections.abc import Iterator


@dataclass
class SourceStatistics:
    """Resultados del análisis de una fuente de caracteres.

    Attributes:
        counts: Cantidad de apariciones por carácter Unicode.
        probabilities: Probabilidad por carácter Unicode.
        total_symbols: Cantidad total de caracteres de la fuente.
        entropy: Entropía de la fuente en bits por símbolo.
    """

    counts: dict[str, int]
    probabilities: dict[str, float]
    total_symbols: int
    entropy: float


@dataclass
class CodeStatistics:
    """Características de las palabras del código Huffman.

    Attributes:
        minimum_length: Límite inferior teórico del largo promedio, H(X),
            en bits por símbolo; no es la palabra más corta.
        average_length: Longitud promedio ponderada en bits por símbolo.
        variance: Varianza de las longitudes ponderada por probabilidad,
            en bits cuadrados.
        is_prefix_code: Indica si ninguna palabra es prefijo de otra.
    """

    minimum_length: float
    average_length: float
    variance: float
    is_prefix_code: bool


@dataclass
class HuffmanResult:
    """Código Huffman y sus estadísticas.

    Attributes:
        codebook: Palabra binaria de cada carácter Unicode.
        statistics: Características del código construido.
    """

    codebook: dict[str, str]
    statistics: CodeStatistics


@dataclass
class EncodedSource:
    """Representación inicial de la fuente codificada.

    Attributes:
        bits: Secuencia binaria representada por caracteres '0' y '1'.
    """

    bits: str

    def iter_codewords(self, codebook: dict[str, str]) -> Iterator[str]:
        """Recorre las palabras binarias sin duplicar toda la salida.

        Args:
            codebook: Código prefijo válido usado para codificar la fuente.

        Yields:
            Palabra binaria correspondiente a cada carácter, en orden.

        Raises:
            ValueError: Si quedan bits sin formar una palabra completa.
        """
        words = set(codebook.values())
        start = 0
        for end in range(1, len(self.bits) + 1):
            word = self.bits[start:end]
            if word in words:
                yield word
                start = end
        if start != len(self.bits):
            raise ValueError("Palabra binaria incompleta o incompatible.")


@dataclass
class FileComparison:
    """Resultado de comparar la fuente original y la recibida.

    Attributes:
        identical: Indica igualdad exacta de ambas secuencias de caracteres.
        original_size: Tamaño original en caracteres.
        received_size: Tamaño recibido en caracteres.
    """

    identical: bool
    original_size: int
    received_size: int


@dataclass
class SourceReport:
    """Fila de la tabla de símbolos del informe B.

    Attributes:
        symbol: Carácter de la fuente (un punto de código Unicode).
        count: Cantidad de apariciones del símbolo.
        probability: Probabilidad del símbolo.
        huffman_code: Palabra binaria asignada al símbolo.
    """

    symbol: str
    count: int
    probability: float
    huffman_code: str


@dataclass
class CodingReport:
    """Resultados necesarios para comparar Huffman con un código fijo.

    Attributes:
        entropy: Entropía en bits por símbolo.
        minimum_length: Límite inferior teórico del largo promedio, H(X),
            en bits por símbolo.
        average_length: Longitud promedio de Huffman en bits por símbolo.
        variance: Varianza de longitudes en bits cuadrados.
        efficiency: Cociente adimensional entre entropía y longitud promedio.
        fixed_code_length: Longitud fija de referencia: 8 bits por símbolo.
        huffman_total_bits: Cantidad de bits de la secuencia codificada.
        fixed_total_bits: Cantidad de símbolos multiplicada por 8 bits.
        fixed_encoding: Tabla de referencia de un byte por carácter.
        fixed_representable: Si todos los caracteres caben en esa tabla.
    """

    entropy: float
    minimum_length: float
    average_length: float
    variance: float
    efficiency: float
    fixed_code_length: int
    huffman_total_bits: int
    fixed_total_bits: int
    fixed_encoding: str = "cp1252"
    fixed_representable: bool = True
