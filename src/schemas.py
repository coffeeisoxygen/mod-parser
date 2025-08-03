import re

from pydantic import BaseModel, ConfigDict, Field, field_validator

ALLOWED_COLUMNS = {"productid", "productname", "quota", "total_"}


class ListParseRequest(BaseModel):
    model_config = ConfigDict(extra="allow", str_strip_whitespace=True)

    mod: str = Field(..., description="Nama modul target (misal digipos)")
    end: str = Field(..., description="Endpoint target (misal list_paket)")
    to: str = Field(..., description="Nomor HP tujuan (format 08... atau 628...)")
    trxid: str = Field(..., description="Transaction ID unik per request")
    kolom: str | None = Field(
        default=None,
        description="Kolom output (opsional): productId, productName, quota, total_",
        examples=["productId,productName,quota,total_"],
    )

    @field_validator("kolom")
    @classmethod
    def validate_kolom(cls, v: str | None) -> str | None:
        if v is None:
            return v
        kolom_set = {k.strip().lower() for k in v.split(",") if k.strip()}
        if not kolom_set.issubset(ALLOWED_COLUMNS):
            raise ValueError(
                f"Field 'kolom' hanya boleh kombinasi dari: {', '.join(ALLOWED_COLUMNS)}"
            )
        return v

    @field_validator("to")
    @classmethod
    def validate_phone_number(cls, v: str) -> str:
        if not re.fullmatch(r"(0|62)\d{9,14}", v.strip()):
            raise ValueError("Nomor HP tidak valid (wajib 08... atau 628...)")
        return v


class ListParseResponse(BaseModel):
    model_config = ConfigDict(extra="allow", str_strip_whitespace=True)

    message: str = Field(..., description="Response akhir dalam format string")
