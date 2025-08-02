"""schemas request yg masuk ke api parser."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class TrimRequest(BaseModel):
    """Model request trim, hanya field mandatory."""

    # Konfigurasi untuk allow extra fields
    model_config = ConfigDict(extra="allow")

    # === MANDATORY FIELDS ===
    end: str = Field(
        ..., description="Endpoint tujuan (mandatory)", examples=["list_paket"]
    )
    to: str = Field(
        ..., description="Tujuan dari request (mandatory)", examples=["08123456789"]
    )
    trxid: str = Field(
        ..., description="Transaction ID (mandatory)", examples=["TRX123LIST"]
    )


class TrimResponse(BaseModel):
    """Response dari API trim, fleksibel."""

    model_config = ConfigDict(extra="allow")
    data: Any = Field(..., description="Payload response (bisa dict, list, dsb)")
