"""schemas request yg masuk ke api parser."""

import re
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TrimRequest(BaseModel):
    """Model request trim, hanya field mandatory, semua query string diterima sebagai extra fields."""

    model_config = ConfigDict(extra="allow", str_strip_whitespace=True)

    end: str = Field(
        ..., description="Endpoint tujuan (mandatory)", examples=["list_paket"]
    )
    to: str = Field(
        ...,
        description="Tujuan dari request (mandatory, harus nomor HP Indonesia)",
        examples=["08123456789", "628123456789"],
    )
    trxid: str = Field(
        ..., description="Transaction ID (mandatory)", examples=["TRX123LIST"]
    )

    kolom: str | None = Field(
        None,
        description="Kolom yang ingin ditampilkan (optional, default: semua kolom)",
        examples=["productId,productName"],
    )

    @field_validator("to")
    @classmethod
    def validate_phone_number(cls, v: str) -> str:
        if not re.fullmatch(r"(0|62)\d{9,14}", v):
            raise ValueError(
                "Field 'to' harus nomor HP Indonesia valid (format 08... atau 628...)"
            )
        return v


class TrimResponse(BaseModel):
    """Response dari API trim, fleksibel."""

    model_config = ConfigDict(extra="allow")
    data: Any = Field(..., description="Payload response (bisa dict, list, dsb)")
