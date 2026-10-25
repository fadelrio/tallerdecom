"""Validación activa de tipos, límites y carga de la configuración de modulación."""

import numpy as np
import pytest

from config import ModulationConfig, load_modulation_config, validate_modulation_config


@pytest.mark.parametrize("changes", [
    {"tipo": None}, {"tipo": ["PAM"]}, {"labeling": None}, {"labeling": ["gray"]},
    {"Eb": True}, {"Eb": "1"}, {"Eb": 1j}, {"Eb": None},
    {"code_rate": True}, {"code_rate": "0.5"}, {"code_rate": None},
])
def test_incompatible_field_types(changes: dict[str, object]) -> None:
    """Los errores de tipo se distinguen de los valores fuera del dominio."""
    with pytest.raises(TypeError):
        validate_modulation_config(ModulationConfig(**{"M": 4, "tipo": "PAM", **changes}))


@pytest.mark.parametrize("config", [None, {}, "PAM"])
def test_configuration_type(config: object) -> None:
    """La función requiere la estructura de configuración acordada."""
    with pytest.raises(TypeError, match="ModulationConfig"):
        validate_modulation_config(config)


@pytest.mark.parametrize("rate", [0.5, 1])
def test_valid_numeric_fields_are_not_modified(rate: float) -> None:
    """Valida tasas válidas y escalares NumPy sin convertir los campos."""
    config = ModulationConfig(np.int64(4), "FSK", np.float64(2.0), "binary", rate)
    values = vars(config).copy()
    assert validate_modulation_config(config) is None
    assert vars(config) == values


@pytest.mark.parametrize("M,tipo,Eb,error", [
    (1, "PAM", 1.0, ValueError), (3, "PAM", 1.0, ValueError),
    (2, "QAM", 1.0, ValueError), (2, "PAM", float("inf"), ValueError),
    (2, "PAM", float("nan"), ValueError), (True, "PAM", 1.0, TypeError),
])
def test_loader_uses_complete_validation(M: int, tipo: str, Eb: float, error: type[Exception]) -> None:
    """El cargador ya no acepta M=1 ni energías no finitas."""
    with pytest.raises(error):
        load_modulation_config(M, tipo, Eb)
