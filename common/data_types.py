"""Estructuras compartidas; no realizan cálculos ni validaciones."""

from dataclasses import dataclass
from collections.abc import Iterator

import numpy as np


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
        K_McM: Suma de Kraft - McMillan. Suma de 2^(-longitud) para cada palabra del código Huffman.
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
    K_McM: float = 0.0


@dataclass
class ModulatedData:
    """Datos modulados como vectores en el espacio de señales.

    Los parámetros de la modulación (M, tipo, bits por símbolo, Eb) no se
    guardan acá: viven en la configuración compartida por transmisor y receptor.

    Attributes:
        symbols: Matriz de forma (N, D); cada fila es un símbolo de la
            constelación expresado en una base ortonormal de dimensión D
            (D = 1 para PAM, D = M para FSK ortogonal).
        padding_bits: Ceros agregados al final de la secuencia de bits para
            completar el último bloque de log2(M) bits. El receptor debe
            descartarlos.
    """

    symbols: np.ndarray
    padding_bits: int = 0


@dataclass
class Constellation:
    """Constelación compartida por modulación, demodulación y gráficos.

    Attributes:
        symbols: Coordenadas reales (M, D) en una base ortonormal.
        labels: Palabras binarias asociadas a las filas, en el mismo orden.
            PAM ordenará niveles de menor a mayor; FSK, ejes de base.
    """

    symbols: np.ndarray
    labels: list[str]


@dataclass
class DemodulatedData:
    """Salida futura de las decisiones del receptor.

    Attributes:
        symbols: Coordenadas decididas (N, D), pertenecientes a la constelación;
            conserva también el último símbolo que contenía relleno.
        bits: Cadena binaria recuperada, sin los bits de relleno finales.
    """

    symbols: np.ndarray
    bits: str


@dataclass
class EnergyStatistics:
    """Energías teóricas o estimadas, sin cálculos dentro de la estructura.

    Attributes:
        symbol_energy: Energía media por símbolo de modulación, Es.
        channel_bit_energy: Energía media por bit transmitido de canal, Ec.
        bit_energy: Energía media por bit de información, Eb.
    """

    symbol_energy: float
    channel_bit_energy: float
    bit_energy: float


@dataclass
class ErrorRates:
    """Probabilidades teóricas o frecuencias estimadas de error.

    Attributes:
        symbol_error_rate: Probabilidad o frecuencia de error de símbolo, SER.
        bit_error_rate: Probabilidad o frecuencia de error de bit, BER.
    """

    symbol_error_rate: float
    bit_error_rate: float


@dataclass
class SymbolStatistics:
    """Datos del histograma en el orden de la constelación.

    Attributes:
        labels: Etiquetas de todos los símbolos, incluso los no observados.
        counts: Vector entero (M,) con cantidades de apariciones.
        probabilities: Vector real (M,) de frecuencias relativas observadas.
    """

    labels: list[str]
    counts: np.ndarray
    probabilities: np.ndarray
