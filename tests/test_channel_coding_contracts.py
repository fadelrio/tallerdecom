"""Verifica las interfaces del apartado C antes de implementar los algoritmos."""

from dataclasses import fields, is_dataclass
import importlib
import inspect
from typing import get_type_hints

import numpy as np
import pytest

from common.data_types import (
    ChannelCodeConfig,
    ChannelCodeParameters,
    ChannelWordDecoding,
    DecodedChannel,
    EncodedChannel,
    EncodedSource,
    SyndromeTable,
)
from config import GROUP_4_CHANNEL_CODE


MODULES = (
    "transmitter.channel_encoder",
    "common.channel_code",
    "receiver.channel_decoder",
)

CONTRACTS = (
    (
        "transmitter.channel_encoder",
        "encode_channel_word",
        {"message_bits": str, "code": ChannelCodeConfig, "return": str},
    ),
    (
        "transmitter.channel_encoder",
        "encode_channel",
        {"source": EncodedSource, "code": ChannelCodeConfig, "return": EncodedChannel},
    ),
    (
        "common.channel_code",
        "build_parity_check_matrix",
        {"code": ChannelCodeConfig, "return": np.ndarray},
    ),
    (
        "common.channel_code",
        "build_syndrome_table",
        {"parity_check_matrix": np.ndarray, "return": SyndromeTable},
    ),
    (
        "common.channel_code",
        "calculate_channel_code_parameters",
        {"code": ChannelCodeConfig, "return": ChannelCodeParameters},
    ),
    (
        "receiver.channel_decoder",
        "decode_channel_word",
        {
            "received_word": str,
            "parity_check_matrix": np.ndarray,
            "syndrome_table": SyndromeTable,
            "return": ChannelWordDecoding,
        },
    ),
    (
        "receiver.channel_decoder",
        "decode_channel",
        {
            "received_bits": str,
            "parity_check_matrix": np.ndarray,
            "syndrome_table": SyndromeTable,
            "source_bit_length": int,
            "return": DecodedChannel,
        },
    ),
)


@pytest.mark.parametrize("module_name", MODULES)
def test_channel_coding_modules_import(module_name: str) -> None:
    """Importa cada módulo y comprueba que documenta su responsabilidad."""
    assert inspect.getdoc(importlib.import_module(module_name))


@pytest.mark.parametrize("module_name,name,expected", CONTRACTS)
def test_channel_coding_signatures(
    module_name: str, name: str, expected: dict[str, object],
) -> None:
    """Comprueba firmas anotadas y docstrings sin invocar algoritmos pendientes."""
    function = getattr(importlib.import_module(module_name), name)
    assert get_type_hints(function) == expected

    parameters = inspect.signature(function).parameters
    assert list(parameters) == [key for key in expected if key != "return"]
    for parameter in parameters.values():
        if parameter.name == "source_bit_length":
            assert parameter.kind is inspect.Parameter.KEYWORD_ONLY
        else:
            assert parameter.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
        assert parameter.default is inspect.Parameter.empty

    doc = inspect.getdoc(function)
    assert doc
    for section in ("Args:", "Returns:", "Raises:", "Notes:"):
        assert section in doc
    for parameter in parameters:
        assert f"{parameter}:" in doc


@pytest.mark.parametrize(
    "data_type,expected",
    (
        (ChannelCodeConfig, {"n": int, "k": int, "generator_matrix": np.ndarray}),
        (EncodedChannel, {"bits": str, "source_bit_length": int}),
        (
            ChannelWordDecoding,
            {"corrected_word": str, "syndrome": str, "applied_error": str | None},
        ),
        (
            DecodedChannel,
            {"source": EncodedSource, "detected_blocks": int, "uncorrected_blocks": int},
        ),
        (
            ChannelCodeParameters,
            {"minimum_distance": int, "detectable_errors": int, "correctable_errors": int},
        ),
    ),
)
def test_channel_coding_dataclasses(
    data_type: type, expected: dict[str, object],
) -> None:
    """Comprueba el orden, tipo y documentación de los campos compartidos."""
    assert is_dataclass(data_type)
    assert [field.name for field in fields(data_type)] == list(expected)
    assert get_type_hints(data_type) == expected

    doc = inspect.getdoc(data_type)
    assert doc and "Attributes:" in doc
    for field in expected:
        assert f"{field}:" in doc


def test_syndrome_table_alias() -> None:
    assert SyndromeTable == dict[str, str]


def test_group_4_channel_code() -> None:
    """Verifica los parámetros de la cátedra y el orden de las filas de G."""
    code = GROUP_4_CHANNEL_CODE
    assert isinstance(code, ChannelCodeConfig)
    assert (code.n, code.k) == (10, 4)
    assert isinstance(code.generator_matrix, np.ndarray)
    expected_rows = ("1101001000", "1010100100", "0111010010", "1101110001")
    np.testing.assert_array_equal(
        code.generator_matrix,
        [[int(bit) for bit in row] for row in expected_rows],
    )
