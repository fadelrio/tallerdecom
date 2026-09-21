"""Decodificación de fuente mediante un árbol binario."""

from common.data_types import EncodedSource
from dataclasses import dataclass


@dataclass
class _DecodeNode:
    symbol: str | None = None
    left: "_DecodeNode | None" = None
    right: "_DecodeNode | None" = None

    @property
    def is_leaf(self) -> bool:
        return self.symbol is not None

def decode_source(encoded: EncodedSource, codebook: dict[str, str]) -> str:
    """Reconstruye la secuencia original de símbolos.

    Args:
        encoded: Secuencia binaria representada como cadena de bits.
        codebook: Palabras Huffman asociadas a símbolos caracteres Unicode.

    Returns:
        Texto reconstruido a partir de la secuencia binaria y el código.

    Raises:
        TypeError: Si codebook no es un diccionario.
        ValueError: Si hay bits inválidos, palabras duplicadas, una secuencia
            incompatible o una palabra final incompleta.

    Notes:
        Reconoce palabras y recupera los caracteres originales.
        Se requiere un código prefijo con palabras binarias no vacías y
        caracteres Unicode. La validación de ese contrato aún es incompleta.
        Una secuencia vacía devuelve texto vacío con un código válido.
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
    decoded: list[str] = []
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

    return "".join(decoded)
