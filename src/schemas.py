import re

from pydantic import BaseModel, ConfigDict, Field, field_validator

ALLOWED_COLUMNS = {"productid", "productname", "quota", "total_"}


class TrimRequest(BaseModel):
    model_config = ConfigDict(extra="allow", str_strip_whitespace=True)

    end: str = Field(..., description="Endpoint tujuan", examples=["list_paket"])
    to: str = Field(..., description="No HP tujuan", examples=["08123456789"])
    trxid: str = Field(..., description="Transaction ID", examples=["TRX123LIST"])
    kolom: str | None = Field(
        default=None,
        description="Kolom yang ingin ditampilkan (boleh kombinasi productId,productName,quota,total_)",
    )

    @field_validator("kolom")
    @classmethod
    def validate_kolom(cls, v: str | None) -> str | None:
        if v is None:
            return v
        kolom_set = {k.strip().lower() for k in v.split(",")}
        if not kolom_set.issubset(ALLOWED_COLUMNS):
            raise ValueError(
                f"Field 'kolom' hanya boleh kombinasi dari: {', '.join(ALLOWED_COLUMNS)}"
            )
        return v

    @field_validator("to")
    @classmethod
    def validate_phone_number(cls, v: str) -> str:
        if not re.fullmatch(r"(0|62)\d{9,14}", v.strip()):
            raise ValueError("No HP tidak valid")
        return v
