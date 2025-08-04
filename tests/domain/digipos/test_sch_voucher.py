# type:ignore
import pytest
from pydantic import ValidationError
from src.domain.digipos.sch_voucher import (
    DigiposReqBuyVoucher,
    DigiposReqListVoucher,
    DigiposVoucherResponse,
    PaymentMethodEnum,
)


def test_valid_list_voucher():
    req = DigiposReqListVoucher(
        username="ACCOUNTDIGIPOS",
        to="08123456789",
        trxid="TRX123",
        payment_method=PaymentMethodEnum.LINKAJA,
        markup=1000,
    )
    assert req.category == "VF"
    assert req.payment_method == PaymentMethodEnum.LINKAJA
    assert req.markup == 1000


def test_invalid_list_voucher_category():
    with pytest.raises(ValidationError) as exc_info:
        DigiposReqListVoucher(
            username="ACCOUNTDIGIPOS",
            to="08123456789",
            trxid="TRX123",
            payment_method=PaymentMethodEnum.LINKAJA,
            category="BYU",
        )
    assert "category hanya boleh bernilai 'VF'" in str(exc_info.value)


def test_valid_buy_voucher():
    req = DigiposReqBuyVoucher(
        username="ACCOUNTDIGIPOS",
        to="08123456789",
        trxid="TRX123",
        payment_method=PaymentMethodEnum.NGRS,
        markup=0,
        check=1,
        product_id="00022396",
    )
    assert req.product_id == "00022396"
    assert req.check == 1
    assert req.payment_method == PaymentMethodEnum.NGRS


def test_invalid_markup():
    with pytest.raises(ValidationError) as exc_info:
        DigiposReqBuyVoucher(
            username="ACCOUNTDIGIPOS",
            to="08123456789",
            trxid="TRX123",
            payment_method=PaymentMethodEnum.LINKAJA,
            markup=-100,
            check=0,
            product_id="00022396",
        )
    assert "Markup harga hanya boleh 0 atau lebih besar" in str(exc_info.value)


def test_response_schema_flexible():
    resp = DigiposVoucherResponse(
        data={"voucherList": [{"id": "0001", "price": 10000}]}, price=10000, status="ok"
    )
    assert resp.data["voucherList"][0]["id"] == "0001"
    assert resp.price == 10000
    assert resp.status == "ok"
    # Test extra field
    resp2 = DigiposVoucherResponse(extra_field="extra")
    assert resp2.model_extra["extra_field"] == "extra"
