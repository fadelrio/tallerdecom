"""Decodificación de fuente mediante un árbol binario."""

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
    """Reconstruye la secuencia original de símbolos.

    Args:
        encoded: Secuencia binaria representada como cadena de bits.
        codebook: Palabras Huffman asociadas a símbolos enteros 0..255.

    Returns:
        Bytes reconstruidos a partir de la secuencia binaria y el código.

    Raises:
        TypeError: Si codebook no es un diccionario.
        ValueError: Si hay bits inválidos, palabras duplicadas, una secuencia
            incompatible o una palabra final incompleta.

    Notes:
        Reconoce palabras y recupera bytes sin convertirlos a texto.
        Se requiere un código prefijo con palabras binarias no vacías y
        símbolos 0..255. La validación de ese contrato aún es incompleta.
        Una secuencia vacía devuelve bytes vacíos con un código válido.
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
