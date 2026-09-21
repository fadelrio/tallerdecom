"""Contrato de decodificación de fuente."""

from common.data_types import EncodedSource
from dataclasses import dataclass


@dataclass
class _DecodeNode:
    symbol: int | None = None
    left: "_DecodeNode | None" = None
    right: "_DecodeNode | None" = None

    @property
    def is_leaf(self) -> bool:
        return self.symbol is not None

def decode_source(encoded: EncodedSource, codebook: dict[int, str]) -> bytes:
    """Reconstruirá la secuencia original de símbolos.

    Args:
        encoded: Secuencia binaria representada como cadena de bits.
        codebook: Palabras Huffman asociadas a símbolos enteros 0..255.

    Returns:
        Bytes reconstruidos a partir de la secuencia binaria y el código.

    Raises:
        NotImplementedError: La funcionalidad está pendiente.

    Notes:
        Deberá reconocer las palabras del código y recuperar los símbolos
        originales sin efectuar conversiones de codificación de texto.
    """

    #raise NotImplementedError("Decodificación de fuente pendiente.")

     if not isinstance(codebook, dict):
        raise TypeError("codebook debe ser un diccionario.")

    bits = encoded.bits

    if any(bit not in ("0", "1") for bit in bits):
        raise ValueError("La secuencia contiene bits inválidos.")

    # Construcción del árbol de decodificación.
    root = _DecodeNode()

    for symbol, code in codebook.items():
        node = root

        for bit in code:
            if bit == "0":
                if node.left is None:
                    node.left = _DecodeNode()
                node = node.left
            else:
                if node.right is None:
                    node.right = _DecodeNode()
                node = node.right

        if node.symbol is not None:
            raise ValueError("Código Huffman inválido.")

        node.symbol = symbol

    # Recorrido del árbol.
    decoded = bytearray()
    node = root

    for bit in bits:
        if bit == "0":
            node = node.left
        else:
            node = node.right

        if node is None:
            raise ValueError("Secuencia incompatible con el código Huffman.")

        if node.is_leaf:
            decoded.append(node.symbol)
            node = root

    if node is not root:
        raise ValueError("La secuencia termina con una palabra incompleta.")

    return bytes(decoded)
