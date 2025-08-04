import pytest
from pydantic import ValidationError
from src.schemas.base import BaseDomainRequest


# Valid cases: any string of digits is valid
@pytest.mark.parametrize(
    "to_value",
    [
        "628123456789",
        "08123456789",
        "1234567890",
        "9" * 1,
        "9" * 100,
        "0",
        "62",
        "08123",
    ],
)
def test_base_domain_request_valid_to(to_value: str) -> None:
    req = BaseDomainRequest(username="ACCOUNTDIGIPOS", to=to_value, trxid="21412LIST")
    assert req.to == to_value


# Invalid cases: anything with non-digit characters
@pytest.mark.parametrize(
    "to_value,expected_msg",
    [
        ("ABCDEFGHJKL", "Nomor HP/voucher hanya boleh berisi angka (numbers only)"),
        ("08123abcde", "Nomor HP/voucher hanya boleh berisi angka (numbers only)"),
        ("12345 6789", "Nomor HP/voucher hanya boleh berisi angka (numbers only)"),
        ("123-456789", "Nomor HP/voucher hanya boleh berisi angka (numbers only)"),
        ("", "Nomor HP/voucher hanya boleh berisi angka (numbers only)"),
    ],
)
def test_base_domain_request_invalid_to(to_value: str, expected_msg: str) -> None:
    with pytest.raises(ValidationError) as exc_info:
        BaseDomainRequest(username="ACCOUNTDIGIPOS", to=to_value, trxid="21412LIST")
    assert expected_msg in str(exc_info.value)


def test_username_and_trxid_required() -> None:
    # Missing username
    with pytest.raises(ValidationError):
        BaseDomainRequest(to="08123456789", trxid="21412LIST")  # type: ignore
    # Missing to
    with pytest.raises(ValidationError):
        BaseDomainRequest(username="ACCOUNTDIGIPOS", trxid="21412LIST")  # type: ignore
    # Missing trxid
    with pytest.raises(ValidationError):
        BaseDomainRequest(username="ACCOUNTDIGIPOS", to="08123456789")  # type: ignore


def test_username_length_constraints() -> None:
    # Too short
    with pytest.raises(ValidationError):
        BaseDomainRequest(username="ab", to="08123456789", trxid="21412LIST")
    # Too long
    with pytest.raises(ValidationError):
        BaseDomainRequest(username="a" * 33, to="08123456789", trxid="21412LIST")
    with pytest.raises(ValidationError):
        BaseDomainRequest(username="ab", to="08123456789", trxid="21412LIST")
    # Too long
    with pytest.raises(ValidationError):
        BaseDomainRequest(username="a" * 33, to="08123456789", trxid="21412LIST")
