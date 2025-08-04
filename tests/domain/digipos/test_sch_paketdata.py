import pytest
from pydantic import ValidationError
from src.domain.digipos.sch_paketdata import (
    DigiposReqListPaketData,
    PackageCategoryEnum,
    PaymentMethodEnum,
)


def test_valid_list_paket_data_minimal():
    req = DigiposReqListPaketData(
        username="ACCOUNTDIGIPOS",
        to="08123456789",
        trxid="TRX123",
        category=PackageCategoryEnum.DATA,
        payment_method=PaymentMethodEnum.LINKAJA,
        kolom=["productId", "productName", "quota", "total_"],
    )
    assert req.category == PackageCategoryEnum.DATA
    assert req.payment_method == PaymentMethodEnum.LINKAJA
    assert set(["productId", "productName", "quota", "total_"]).issubset(set(req.kolom))


def test_invalid_payment_method_for_data():
    with pytest.raises(ValidationError) as exc_info:
        DigiposReqListPaketData(
            username="ACCOUNTDIGIPOS",
            to="08123456789",
            trxid="TRX123",
            category=PackageCategoryEnum.DATA,
            payment_method=PaymentMethodEnum.NGRS,
            kolom=["productId", "productName", "quota", "total_"],
        )
    assert "Pembelian Ini Hanya Bisa Dengan Methode LinkAJA" in str(exc_info.value)


def test_invalid_kolom_missing_required():
    with pytest.raises(ValidationError) as exc_info:
        DigiposReqListPaketData(
            username="ACCOUNTDIGIPOS",
            to="08123456789",
            trxid="TRX123",
            category=PackageCategoryEnum.DATA,
            payment_method=PaymentMethodEnum.LINKAJA,
            kolom=["productId", "productName", "quota"],  # missing total_
        )
    assert "Field kolom harus mengandung minimal" in str(exc_info.value)
    assert "Missing: total_" in str(exc_info.value)


def test_valid_with_optional_fields():
    req = DigiposReqListPaketData(
        username="ACCOUNTDIGIPOS",
        to="08123456789",
        trxid="TRX123",
        category=PackageCategoryEnum.DIGITAL_OTHER,
        payment_method=PaymentMethodEnum.LINKAJA,
        kolom=["productId", "productName", "quota", "total_"],
        sub_category="Combo Sakti",
        duration="30 Days",
        markup=5000,
    )
    assert req.sub_category == "Combo Sakti"
    assert req.duration == "30 Days"
    assert req.markup == 5000


def test_default_kolom():
    req = DigiposReqListPaketData(
        username="ACCOUNTDIGIPOS",
        to="08123456789",
        trxid="TRX123",
        category=PackageCategoryEnum.DATA,
        payment_method=PaymentMethodEnum.LINKAJA,
    )
    assert set(["productId", "productName", "quota", "total_"]).issubset(set(req.kolom))


def test_payment_method_enum():
    assert PaymentMethodEnum.LINKAJA == "LINKAJA"
    assert PaymentMethodEnum.NGRS == "NGRS"


def test_category_enum():
    assert PackageCategoryEnum.DATA == "DATA"
    assert PackageCategoryEnum.VOICE_SMS == "VOICE_SMS"
    assert PackageCategoryEnum.DIGITAL_OTHER == "DIGITAL_OTHER"
    assert PackageCategoryEnum.HVC_DATA == "HVC_DATA"


def test_invalid_kolom_multiple_missing():
    with pytest.raises(ValidationError) as exc_info:
        DigiposReqListPaketData(
            username="ACCOUNTDIGIPOS",
            to="08123456789",
            trxid="TRX123",
            category=PackageCategoryEnum.DATA,
            payment_method=PaymentMethodEnum.LINKAJA,
            kolom=["productId"],  # missing productName, quota, total_
        )
    error_message = str(exc_info.value)
    assert "Missing" in error_message
    assert "productName" in error_message
    assert "quota" in error_message
    assert "total_" in error_message
