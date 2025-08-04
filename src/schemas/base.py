from pydantic import BaseModel, ConfigDict, Field, field_validator


class BaseDomainRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    username: str = Field(
        min_length=3,
        max_length=32,
        description="Username of the user making the request, pastikan ini ada di config.toml",
        examples=["ACCOUNTDIGIPOS"],
    )
    to: str = Field(
        description="tujuan transakasi, biasa nya ini adalah nomor handphone / nomor voucher",
        examples=["081298923834", "1214230873"],
    )
    trxid: str = Field(
        description="ID transaksi, ini adalah ID unik yang digunakan untuk mengidentifikasi transaksi",
        examples=["21412LIST", "123124"],
    )

    @field_validator("to", mode="after")
    @classmethod
    def validate_to_isdigit(cls, v: str) -> str:
        value = v.strip()
        if not value.isdigit():
            raise ValueError("Nomor HP/voucher hanya boleh berisi angka (numbers only)")
        return v
