"""Pruebas funcionales de fuente e integración, sin benchmarks."""

from collections.abc import Callable
from typing import ParamSpec, TypeVar

import pytest

from receiver.source_decoder import decode_source
from transmitter.huffman import build_huffman_code
from transmitter.source_analysis import analyze_source
from transmitter.source_encoder import _BLOCK_SIZE, encode_source


# Estos tipos conservan los argumentos y el retorno de la función envuelta;
# el auxiliar puede usarse con análisis, Huffman o decodificación.
_P = ParamSpec("_P")
_T = TypeVar("_T")


def _available(
    function: Callable[_P, _T], *args: _P.args, **kwargs: _P.kwargs
) -> _T:
    """Omite solo llamadas a interfaces que aún lanzan NotImplementedError."""
    try:
        return function(*args, **kwargs)
    except NotImplementedError:
        # Omisión temporal para trabajo en paralelo. Otros errores deben
        # fallar: no queremos ocultar defectos de una implementación real.
        pytest.skip(f"{function.__name__} todavía está pendiente")


@pytest.mark.parametrize(
    "data, codebook, expected",
    [
        ('', {}, ""),
        ('ABA', {'A': "0", 'B': "10"}, "0100"),
        ('\x00ÿ\n\x00', {'\x00': "0", 'ÿ': "10", '\n': "11"}, "010110"),
        ('AAAA', {'A': "0"}, "0000"),
        ("".join(map(chr, range(256))), {chr(i): f"{i:08b}" for i in range(256)},
         "".join(f"{i:08b}" for i in range(256))),
    ],
)
def test_encode_examples(
    data: str, codebook: dict[str, str], expected: str
) -> None:
    """Comprueba palabras conocidas, entrada vacía y todo el conjunto de caracteres de prueba.

    Args:
        data: Fuente de ejemplo.
        codebook: Código prefijo manual válido.
        expected: Secuencia binaria esperada.
    """
    # El diccionario también se usará para decodificar; codificar no debe
    # modificarlo. Los códigos manuales aíslan esta prueba de Huffman.
    original_codebook = codebook.copy()
    assert encode_source(data, codebook).bits == expected
    assert codebook == original_codebook


@pytest.mark.parametrize("size", [_BLOCK_SIZE - 1, _BLOCK_SIZE,
                                  _BLOCK_SIZE + 1, 2 * _BLOCK_SIZE + 3])
def test_encode_block_boundaries(size: int) -> None:
    """Verifica orden y continuidad antes, en y después del límite de bloque.

    Args:
        size: Cantidad de caracteres del caso de prueba.
    """
    # El patrón de tres caracteres cruza los límites de 65536 caracteres y permite detectar
    # pérdidas, duplicaciones o cambios de orden al unir bloques.
    data = ('ABA' * ((size + 2) // 3))[:size]
    whole, remainder = divmod(size, 3)
    # Cada ABA produce 0100. El resto es vacío, A (0) o AB (010).
    # Así obtenemos el esperado sin repetir el algoritmo del codificador.
    expected = "0100" * whole + ("", "0", "010")[remainder]
    assert encode_source(data, {'A': "0", 'B': "10"}).bits == expected


@pytest.mark.parametrize("prefix_size", [0, _BLOCK_SIZE])
def test_encode_missing_symbol(prefix_size: int) -> None:
    """Rechaza símbolos faltantes incluso después de procesar otro bloque.

    Args:
        prefix_size: Cantidad de símbolos válidos anteriores al error.
    """
    with pytest.raises(ValueError, match="ÿ"):
        encode_source('A' * prefix_size + 'ÿ', {'A': "0"})


def test_source_analysis_and_encoding() -> None:
    """Comprueba estadísticas conocidas y codificación con código manual.

    Notes:
        Se activa al implementar analyze_source, sin depender de Huffman.
    """
    data = '\x00ÿ\x00\n'
    statistics = _available(analyze_source, data)
    assert statistics.counts == {'\x00': 2, 'ÿ': 1, '\n': 1}
    assert statistics.probabilities == pytest.approx(
        {'\x00': 0.5, 'ÿ': 0.25, '\n': 0.25}
    )
    assert statistics.total_symbols == 4
    # H = -(0.5 * log2(0.5) + 2 * 0.25 * log2(0.25)) = 1.5.
    # approx admite diferencias de redondeo de punto flotante.
    assert statistics.entropy == pytest.approx(1.5)
    encoded = encode_source(data, {'\x00': "0", 'ÿ': "10", '\n': "11"})
    assert encoded.bits == "010011"


@pytest.mark.parametrize("data, codebook", [
    ('ABA', {'A': "0", 'B': "10"}),
    ('\x00ÿ\n' * (_BLOCK_SIZE // 3 + 1),
     {'\x00': "0", 'ÿ': "10", '\n': "11"}),
])
def test_source_round_trip(data: str, codebook: dict[str, str]) -> None:
    """Comprueba recuperación exacta cuando esté disponible el decodificador.

    Args:
        data: Caracteres originales, incluidos controles y varios bloques.
        codebook: Código prefijo conocido independiente de Huffman.
    """
    encoded = encode_source(data, codebook)
    received = _available(decode_source, encoded, codebook)
    assert isinstance(received, str)
    assert received == data


def test_full_transmitter() -> None:
    """Integra análisis, Huffman y codificación cuando estén disponibles.

    Notes:
        No exige palabras específicas ante empates de Huffman. La fuente
        tiene probabilidades 1/2, 1/4, 1/4 y longitud óptima de seis bits.
    """
    data = '\x00ÿ\x00\n'
    statistics = _available(analyze_source, data)
    huffman = _available(build_huffman_code, statistics.probabilities)
    assert set(huffman.codebook) == set(data)
    words = list(huffman.codebook.values())
    assert all(word and set(word) <= {"0", "1"} for word in words)
    # Ninguna palabra debe ser prefijo de otra; se excluye la comparación
    # consigo misma. No fijamos qué símbolo recibe 0 o 1 ante un empate.
    assert all(not right.startswith(left)
               for i, left in enumerate(words)
               for j, right in enumerate(words) if i != j)
    encoded = encode_source(data, huffman.codebook)
    # Con frecuencias 2, 1, 1, Huffman asigna longitudes 1, 2, 2:
    # el total esperado es 2 * 1 + 1 * 2 + 1 * 2 = 6 bits.
    assert len(encoded.bits) == 6
    assert encoded.bits == "".join(huffman.codebook[symbol] for symbol in data)
    assert huffman.statistics.average_length == pytest.approx(1.5)


def test_full_source_round_trip() -> None:
    """Integra todos los módulos de fuente una vez implementados."""
    data = "".join(map(chr, range(256))) * 2
    statistics = _available(analyze_source, data)
    huffman = _available(build_huffman_code, statistics.probabilities)
    encoded = encode_source(data, huffman.codebook)
    received = _available(decode_source, encoded, huffman.codebook)
    assert received == data


@pytest.mark.parametrize("probabilities, expected", [
    ({}, 0.0), ({'\x00': 1.0, '\x01': 0.0}, 0.0),
    ({'\x00': 0.5, '\x01': 0.5}, 1.0),
])
def test_entropy_zero_terms(
    probabilities: dict[str, float], expected: float
) -> None:
    """Comprueba entropía conocida sin evaluar logaritmos de cero.

    Args:
        probabilities: Distribución de ejemplo.
        expected: Entropía esperada en bits por símbolo.
    """
    from transmitter.source_analysis import calculate_entropy

    assert calculate_entropy(probabilities) == pytest.approx(expected)


def test_entropy_negative_probability() -> None:
    """Rechaza probabilidades negativas en lugar de omitirlas."""
    from transmitter.source_analysis import calculate_entropy

    with pytest.raises(ValueError):
        calculate_entropy({'\x00': -0.5, '\x01': 1.5})


@pytest.mark.parametrize("entropy, length, expected", [
    (1.5, 2.0, 0.75), (0.0, 1.0, 0.0), (1.0, 1.0, 1.0),
])
def test_efficiency(entropy: float, length: float, expected: float) -> None:
    """Verifica eficiencia como fracción, incluida entropía cero.

    Args:
        entropy: Entropía de ejemplo.
        length: Longitud promedio de ejemplo.
        expected: Fracción esperada.
    """
    from transmitter.huffman import calculate_efficiency

    assert calculate_efficiency(entropy, length) == pytest.approx(expected)


@pytest.mark.parametrize("entropy, length", [(-1.0, 1.0), (1.0, 0.0),
                                           (1.0, -1.0)])
def test_efficiency_invalid(entropy: float, length: float) -> None:
    """Verifica el rechazo de argumentos fuera del dominio documentado.

    Args:
        entropy: Entropía de entrada.
        length: Longitud promedio de entrada.
    """
    from transmitter.huffman import calculate_efficiency

    with pytest.raises(ValueError):
        calculate_efficiency(entropy, length)


def test_empty_source_contracts() -> None:
    """El análisis admite vacío, pero Huffman conserva su rechazo explícito."""
    statistics = analyze_source('')
    assert statistics.counts == statistics.probabilities == {}
    assert statistics.total_symbols == 0
    assert statistics.entropy == 0.0
    with pytest.raises(ValueError, match="vacía"):
        build_huffman_code(statistics.probabilities)


@pytest.mark.parametrize("text", ["ááñ", "Hola, 世界 👋\r\n\t", "e\u0301é", "aaaa"])
def test_unicode_round_trip(text: str) -> None:
    """Preserva puntos de código, controles y texto sin normalización.

    Args:
        text: Fuente Unicode de ejemplo.
    """
    stats = analyze_source(text)
    assert stats.total_symbols == len(text)
    code = build_huffman_code(stats.probabilities)
    encoded = encode_source(text, code.codebook)
    assert list(encoded.iter_codewords(code.codebook)) == [
        code.codebook[character] for character in text
    ]
    assert decode_source(encoded, code.codebook) == text


def test_accent_is_one_symbol() -> None:
    """Los bytes UTF-8 de un acento no se cuentan como símbolos separados."""
    stats = analyze_source("ááñ")
    assert stats.counts == {"á": 2, "ñ": 1}
    assert stats.total_symbols == 3
