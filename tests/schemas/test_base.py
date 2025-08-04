import pytest
from pydantic import ValidationError
from src.schemas.base_schemas import BaseDomainRequest


def test_valid_base_domain_request():
    req = BaseDomainRequest(username="User123", to="081234567890", trxid="TRX123")
    assert req.username == "User123"
    assert req.to == "081234567890"
    assert req.trxid == "TRX123"


@pytest.mark.parametrize("username", ["ab", "a" * 33])
def test_username_length_invalid(username):
    with pytest.raises(ValidationError) as exc:
        BaseDomainRequest(username=username, to="081234567890", trxid="TRX123")
    assert "String should have at least 3 characters" in str(
        exc.value
    ) or "String should have at most 32 characters" in str(exc.value)


@pytest.mark.parametrize("username", ["user!", "user name", "user@123"])
def test_username_non_alphanumeric(username):
    with pytest.raises(ValidationError) as exc:
        BaseDomainRequest(username=username, to="081234567890", trxid="TRX123")
    assert "Username hanya boleh berisi angka dan huruf" in str(exc.value)


@pytest.mark.parametrize("trxid", ["trx-123", "trx id", "trx@123"])
def test_trxid_non_alphanumeric(trxid):
    with pytest.raises(ValidationError) as exc:
        BaseDomainRequest(username="User123", to="081234567890", trxid=trxid)
    assert "ID transaksi hanya boleh berisi angka dan huruf" in str(exc.value)


@pytest.mark.parametrize("to", ["08123abc", "123 456", "0812-3456"])
def test_to_not_digit(to):
    with pytest.raises(ValidationError) as exc:
        BaseDomainRequest(username="User123", to=to, trxid="TRX123")
    assert "Nomor HP/voucher hanya boleh berisi angka" in str(exc.value)


def test_extra_fields_allowed():
    req = BaseDomainRequest(
        username="User123",
        to="081234567890",
        trxid="TRX123",
        extra_field="extra",  # type: ignore
    )
    assert req.model_extra["extra_field"] == "extra"  # type: ignore
