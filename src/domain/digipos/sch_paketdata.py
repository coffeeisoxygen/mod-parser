from enum import StrEnum

from pydantic import Field, field_validator, model_validator

from src.schemas.base import BaseDomainRequest


class PackageCategoryEnum(StrEnum):
    """category yang boleh user pilih di request."""

    DATA = "DATA"
    VOICE_SMS = "VOICE_SMS"
    DIGITAL_OTHER = "DIGITAL_OTHER"
    DIGITAL_MUSIC = "DIGITAL_MUSIC"
    DIGITAL_GAME = "DIGITAL_GAME"
    ROAMING = "ROAMING"
    VF = "VF"
    BYU = "BYU"
    HVC_DATA = "HVC_DATA"
    HVC_VOICE_SMS = "HVC_VOICE_SMS"


class PaymentMethodEnum(StrEnum):
    """payment method yang boleh user pilih di request."""

    LINKAJA = "LINKAJA"
    NGRS = "NGRS"


class DigiposReqListPaketData(BaseDomainRequest):
    """Request Schemas ketika user ingin memlihat List Paket eligible untuk nomor tujuan."""

    category: PackageCategoryEnum = Field(
        description="Kategori paket yang ingin dilihat, seperti DATA, VOICE_SMS, DIGITAL_OTHER, dll.",
        examples=[PackageCategoryEnum.DATA, PackageCategoryEnum.VOICE_SMS],
    )
    sub_category: str | None = Field(
        default=None,
        description="Subkategori produk, jika ada. Misalnya, untuk kategori DATA bisa berupa Combo Sakti Dan Lain Lain.",
        examples=["Combo Sakti", "Lain Lain", None],
    )

    duration: str | None = Field(
        default=None,
        description="Durasi paket, jika ada. Misalnya, '30 hari', '7 hari'.",
        examples=["30 Days", "7 Days", None],
    )
    payment_method: PaymentMethodEnum = Field(
        description="Metode pembayaran yang digunakan, seperti LINKAJA atau NGRS.",
        examples=[PaymentMethodEnum.LINKAJA, PaymentMethodEnum.NGRS],
    )

    up_harga: int | None = Field(
        default=0,
        description="Harga Untuk Melakukan Markup kepada harga paket data.",
        examples=[0, 10000],
    )

    kolom: list[str] = Field(
        default_factory=lambda: ["productId", "productName", "quota", "total_"]
    )

    @model_validator(mode="after")
    def validate_rules(self) -> "DigiposReqListPaketData":
        # 1. Validasi untuk paket DATA
        if (
            self.category == PackageCategoryEnum.DATA
            and self.payment_method != PaymentMethodEnum.LINKAJA
        ):
            raise ValueError(
                "Paket DATA hanya boleh menggunakan LINKAJA sebagai payment_method."
            )

        # 2. Validasi untuk kolom wajib
        required = {"productId", "productName", "quota", "total_"}
        if not required.issubset(set(self.kolom)):
            missing = required - set(self.kolom)
            raise ValueError(
                f"Field kolom harus mengandung minimal: {', '.join(required)}. Missing: {', '.join(missing)}"
            )

        return self


class DigiposReqBuyPaketData(BaseDomainRequest):
    """Request Schemas ketika user ingin membeli Paket Data."""

    category: PackageCategoryEnum = Field(
        description="Kategori paket yang ingin dibeli, seperti DATA, VOICE_SMS, DIGITAL_OTHER, dll.",
        examples=[PackageCategoryEnum.DATA, PackageCategoryEnum.VOICE_SMS],
    )

    product_id: str = Field(
        description="ID produk paket data yang ingin dibeli.",
        examples=["1234567890"],
    )
    payment_method: PaymentMethodEnum = Field(
        description="Metode pembayaran yang digunakan, seperti LINKAJA atau NGRS.",
        examples=[PaymentMethodEnum.LINKAJA, PaymentMethodEnum.NGRS],
    )
    check: int = Field(
        description="Apakah ingin melakukan pengecekan sebelum pembelian? 1 untuk ya, 0 untuk tidak.",
        examples=[1, 0],
    )
    up_harga: int | None = Field(
        default=0,
        description="Harga Untuk Melakukan Markup kepada harga paket data.",
        examples=[0, 10000],
    )

    @field_validator("check")
    @classmethod
    def validate_check(cls, v: int) -> int:
        if v not in (0, 1):
            raise ValueError("Field 'check' hanya boleh bernilai 0 atau 1.")
        return v

    @model_validator(mode="after")
    def check_payment_method(self) -> "DigiposReqBuyPaketData":
        if self.payment_method == PaymentMethodEnum.NGRS:
            raise ValueError("Pembelian paket data hanya mendukung LINKAJA saat ini.")
        return self
