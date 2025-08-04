# type: ignore
import pytest
from pydantic import ValidationError
from src.domain.digipos.sch_paketdata import (
    DigiposReqBuyPaketData,
    PackageCategoryEnum,
    PaymentMethodEnum,
)


def test_valid_buy_paket_data_minimal():
    req = DigiposReqBuyPaketData(
        username="ACCOUNTDIGIPOS",
        to="08123456789",
        trxid="TRX123",
        category=PackageCategoryEnum.DATA,
        product_id="00017864",
        payment_method=PaymentMethodEnum.LINKAJA,
        check=0,
    )
    assert req.category == PackageCategoryEnum.DATA
    assert req.product_id == "00017864"
    assert req.payment_method == PaymentMethodEnum.LINKAJA
    assert req.up_harga == 0
    assert req.check == 0


def test_valid_buy_paket_data_with_optional():
    req = DigiposReqBuyPaketData(
        username="ACCOUNTDIGIPOS",
        to="08123456789",
        trxid="TRX123",
        category=PackageCategoryEnum.DIGITAL_OTHER,
        product_id="00017864",
        payment_method=PaymentMethodEnum.LINKAJA,
        check=1,
        up_harga=5000,
    )
    assert req.check == 1
    assert req.up_harga == 5000


def test_invalid_payment_method_ngrs():
    with pytest.raises(ValidationError) as exc_info:
        DigiposReqBuyPaketData(
            username="ACCOUNTDIGIPOS",
            to="08123456789",
            trxid="TRX123",
            category=PackageCategoryEnum.DATA,
            product_id="00017864",
            payment_method=PaymentMethodEnum.NGRS,
            check=1,
        )
    assert "Pembelian paket data hanya mendukung LINKAJA" in str(exc_info.value)


def test_missing_required_fields():
    # Missing product_id
    with pytest.raises(ValidationError) as exc_info:
        DigiposReqBuyPaketData(
            username="ACCOUNTDIGIPOS",
            to="08123456789",
            trxid="TRX123",
            category=PackageCategoryEnum.DATA,
            payment_method=PaymentMethodEnum.LINKAJA,
            check=1,
            # product_id missing
        )
    assert "Field required" in str(exc_info.value)
    # Missing category
    with pytest.raises(ValidationError) as exc_info:
        DigiposReqBuyPaketData(
            username="ACCOUNTDIGIPOS",
            to="08123456789",
            trxid="TRX123",
            product_id="00017864",
            payment_method=PaymentMethodEnum.LINKAJA,
            check=1,
            # category missing
        )
    assert "Field required" in str(exc_info.value)
    # Missing payment_method
    with pytest.raises(ValidationError) as exc_info:
        DigiposReqBuyPaketData(
            username="ACCOUNTDIGIPOS",
            to="08123456789",
            trxid="TRX123",
            category=PackageCategoryEnum.DATA,
            product_id="00017864",
            check=1,
            # payment_method missing
        )
    assert "Field required" in str(exc_info.value)
    # Missing check
    with pytest.raises(ValidationError) as exc_info:
        DigiposReqBuyPaketData(
            username="ACCOUNTDIGIPOS",
            to="08123456789",
            trxid="TRX123",
            category=PackageCategoryEnum.DATA,
            product_id="00017864",
            payment_method=PaymentMethodEnum.LINKAJA,
            # check missing
        )
    assert "Field required" in str(exc_info.value)


def test_invalid_enum_value():
    # payment_method salah
    with pytest.raises(ValueError):
        DigiposReqBuyPaketData(
            username="ACCOUNTDIGIPOS",
            to="08123456789",
            trxid="TRX123",
            category=PackageCategoryEnum.DATA,
            product_id="00017864",
            payment_method="SALAH",  # type: ignore
            check=1,
        )
    # category salah
    with pytest.raises(ValueError):
        DigiposReqBuyPaketData(
            username="ACCOUNTDIGIPOS",
            to="08123456789",
            trxid="TRX123",
            category="SALAH",  # type: ignore
            product_id="00017864",
            payment_method=PaymentMethodEnum.LINKAJA,
            check=1,
        )


def test_invalid_check_value():
    # check < 0
    with pytest.raises(ValidationError) as exc_info:
        DigiposReqBuyPaketData(
            username="ACCOUNTDIGIPOS",
            to="08123456789",
            trxid="TRX123",
            category=PackageCategoryEnum.DATA,
            product_id="00017864",
            payment_method=PaymentMethodEnum.LINKAJA,
            check=-1,
        )
    assert "Field 'check' hanya boleh bernilai 0 atau 1" in str(exc_info.value)
    # check > 1
    with pytest.raises(ValidationError) as exc_info:
        DigiposReqBuyPaketData(
            username="ACCOUNTDIGIPOS",
            to="08123456789",
            trxid="TRX123",
            category=PackageCategoryEnum.DATA,
            product_id="00017864",
            payment_method=PaymentMethodEnum.LINKAJA,
            check=2,
        )
    assert "Field 'check' hanya boleh bernilai 0 atau 1" in str(exc_info.value)
