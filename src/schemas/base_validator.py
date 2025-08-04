from typing import Annotated

from pydantic import Field, PositiveInt, field_validator


def validate_check(v: int) -> int:
    """Validator for the 'check' field to ensure it is either 0 or 1."""
    if v not in (0, 1):
        raise ValueError("Field 'check' hanya boleh bernilai 0 atau 1.")
    return v


CheckInt = Annotated[
    int, Field(description="Check 0/1"), field_validator("check")(validate_check)
]


def validate_only_alnumeric(v: str) -> str:
    """Validator to ensure a string is alphanumeric."""
    if not v.isalnum():
        raise ValueError("Hanya boleh berisi angka dan huruf (alphanumeric only)")
    return v


FiledAlNum = Annotated[
    str,
    Field(description="Hanya boleh berisi angka dan huruf (alphanumeric only)"),
    field_validator("username", "trxid")(validate_only_alnumeric),
]


def validate_phone_number(v: str) -> str:
    """Validator for phone numbers to ensure they start with '08' or '628'."""
    if not (v.startswith("08") or v.startswith("628")):
        raise ValueError("Nomor telepon harus dimulai dengan '08' atau '628'.")
    return v


PhoneNumberStr = Annotated[
    str,
    Field(description="Nomor telepon"),
    field_validator("phone_number")(validate_phone_number),
]


UpHargaInt = Annotated[PositiveInt, Field(default=0, ge=0, description="Harga markup")]
