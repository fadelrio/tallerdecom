"""Ejecución de casos funcionales que esperan interfaces todavía pendientes."""

from collections.abc import Callable
from typing import ParamSpec, TypeVar

import pytest


_P = ParamSpec("_P")
_T = TypeVar("_T")


def available(function: Callable[_P, _T], *args: _P.args, **kwargs: _P.kwargs) -> _T:
    """Omite solamente la llamada que todavía lanza NotImplementedError.

    Args:
        function: Función pendiente o implementada que se quiere comprobar.
        args: Argumentos posicionales del caso.
        kwargs: Argumentos nombrados del caso.

    Returns:
        Resultado de una función implementada, para verificarlo fuera del try.

    Notes:
        No envolver las aserciones: otros errores y resultados incorrectos
        deben fallar. No omite permanentemente los casos funcionales.
    """
    try:
        return function(*args, **kwargs)
    except NotImplementedError as error:
        pytest.skip(f"{function.__name__}: {error}")
