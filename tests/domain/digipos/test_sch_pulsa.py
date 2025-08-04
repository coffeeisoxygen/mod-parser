# type:ignore
import pytest
from pydantic import ValidationError
from src.domain.digipos.sch_pulsa import (
    DigiposPulsaResponse,
    DigiposReqBuyPulsa,
    DigiposReqListPulsa,
    PaymentMethodEnum,
    PulsaPackageCategoryEnum,
)


def test_valid_list_pulsa():
    req = DigiposReqListPulsa(
        username="ACCOUNTDIGIPOS",
        to="08123456789",
        trxid="TRX123",
        amount=10000,
        payment_method=PaymentMethodEnum.LINKAJA,
        up_harga=2000,
    )
    assert req.amount == 10000
    assert req.payment_method == PaymentMethodEnum.LINKAJA
    assert req.up_harga == 2000


def test_invalid_list_pulsa_payment_method():
    with pytest.raises(ValidationError) as exc_info:
        DigiposReqListPulsa(
            username="ACCOUNTDIGIPOS",
            to="08123456789",
            trxid="TRX123",
            amount=10000,
            payment_method=PaymentMethodEnum.NGRS,
        )
    assert "Pulsa hanya boleh menggunakan LINKAJA" in str(exc_info.value)


def test_valid_buy_pulsa_fix():
    req = DigiposReqBuyPulsa(
        username="ACCOUNTDIGIPOS",
        to="08123456789",
        trxid="TRX123",
        category=PulsaPackageCategoryEnum.FIX,
        payment_method=PaymentMethodEnum.NGRS,
        up_harga=0,
        check=1,
    )
    assert req.category == PulsaPackageCategoryEnum.FIX
    assert req.payment_method == PaymentMethodEnum.NGRS
    assert req.check == 1


def test_valid_buy_pulsa_bulk():
    req = DigiposReqBuyPulsa(
        username="ACCOUNTDIGIPOS",
        to="08123456789",
        trxid="TRX123",
        category=PulsaPackageCategoryEnum.BULK,
        payment_method=PaymentMethodEnum.LINKAJA,
        up_harga=1000,
        check=0,
    )
    assert req.category == PulsaPackageCategoryEnum.BULK
    assert req.payment_method == PaymentMethodEnum.LINKAJA
    assert req.up_harga == 1000
    assert req.check == 0


def test_invalid_buy_pulsa_category_payment():
    #  but payment_method != NGRS
    with pytest.raises(ValidationError) as exc_info:
        DigiposReqBuyPulsa(
            username="ACCOUNTDIGIPOS",
            to="08123456789",
            trxid="TRX123",
            category=PulsaPackageCategoryEnum.FIX,
            payment_method=PaymentMethodEnum.LINKAJA,
            up_harga=0,
            check=1,
        )
    assert "category FIX, payment_method wajib NGRS" in str(exc_info.value)
    # BULK but payment_method != LINKAJA
    with pytest.raises(ValidationError) as exc_info:
        DigiposReqBuyPulsa(
            username="ACCOUNTDIGIPOS",
            to="08123456789",
            trxid="TRX123",
            category=PulsaPackageCategoryEnum.BULK,
            payment_method=PaymentMethodEnum.NGRS,
            up_harga=0,
            check=0,
        )
    assert "category BULK, payment_method wajib LINKAJA" in str(exc_info.value)


def test_response_schema_flexible():
    # Test with data field
    resp = DigiposPulsaResponse(
        data={"rechargeDenomList": [{"denom_type": "BULK", "total_price": 6519}]}
    )
    assert resp.data["rechargeDenomList"][0]["denom_type"] == "BULK"
    # Test with req, price, salAkhir fields
    resp2 = DigiposPulsaResponse(
        req={"username": "WIR6289504"}, price=5519, salAkhir="3230"
    )
    assert resp2.price == 5519
    assert resp2.salAkhir == "3230"
    # Test with extra fields (should not raise)
    resp3 = DigiposPulsaResponse(extra_field="extra")
    assert resp3.extra_field == "extra"
