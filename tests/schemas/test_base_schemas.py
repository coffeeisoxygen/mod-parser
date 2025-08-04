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
    assert req.to.isdigit()  # Ensure that 'to' is a digit string


# Invalid cases: anything with non-digit characters


def test_base_domain_request_invalid_username_empty() -> None:
    # Username kosong: harus error min_length, bukan pesan custom validator
    with pytest.raises(ValidationError) as exc_info:
        BaseDomainRequest(username="", to="08123456789", trxid="21412LIST")
    assert "ensure this value has at least 3 characters" in str(exc_info.value)


@pytest.mark.parametrize(
    "username_value",
    [
        "user name",
        "user-name",
        "user_name",
        "user@123",
        "user.123",
        "user!",
    ],
)
def test_base_domain_request_invalid_username_non_alnum(username_value: str) -> None:
    with pytest.raises(ValidationError) as exc_info:
        BaseDomainRequest(username=username_value, to="08123456789", trxid="21412LIST")
    assert "Username hanya boleh berisi angka dan huruf (alphanumeric only)" in str(
        exc_info.value
    )
    # Missing trxid
    with pytest.raises(ValidationError) as exc_info:
        BaseDomainRequest(username="ACCOUNTDIGIPOS", to="08123456789")  # type: ignore
    assert "field required" in str(exc_info.value)


def test_username_length_constraints() -> None:
    # Too short
    with pytest.raises(ValidationError) as exc_info:
        BaseDomainRequest(username="ab", to="08123456789", trxid="21412LIST")
    assert "ensure this value has at least 3 characters" in str(exc_info.value)
    # Too long
    with pytest.raises(ValidationError) as exc_info:
        BaseDomainRequest(username="a" * 33, to="08123456789", trxid="21412LIST")
    assert "ensure this value has at most 32 characters" in str(exc_info.value)
    with pytest.raises(ValidationError):
        BaseDomainRequest(username="ab", to="08123456789", trxid="21412LIST")
    # Too long
    with pytest.raises(ValidationError):
        BaseDomainRequest(username="a" * 33, to="08123456789", trxid="21412LIST")


@pytest.mark.parametrize(
    "trxid_value",
    [
        "21412LIST",
        "123124",
        "abcDEF123",
        "A1B2C3",
        "0",
        "a",
        "Z9",
        "1234567890",
    ],
)
def test_base_domain_request_valid_trxid(trxid_value: str) -> None:
    req = BaseDomainRequest(
        username="ACCOUNTDIGIPOS", to="08123456789", trxid=trxid_value
    )
    assert req.trxid == trxid_value


@pytest.mark.parametrize(
    "trxid_value,expected_msg",
    [
        ("", "ID transaksi hanya boleh berisi angka dan huruf (alphanumeric only)"),
        (
            "123 456",
            "ID transaksi hanya boleh berisi angka dan huruf (alphanumeric only)",
        ),
        (
            "abc-123",
            "ID transaksi hanya boleh berisi angka dan huruf (alphanumeric only)",
        ),
        (
            "abc_123",
            "ID transaksi hanya boleh berisi angka dan huruf (alphanumeric only)",
        ),
        (
            "@trxid!",
            "ID transaksi hanya boleh berisi angka dan huruf (alphanumeric only)",
        ),
    ],
)
def test_base_domain_request_invalid_trxid(trxid_value: str, expected_msg: str) -> None:
    with pytest.raises(ValidationError) as exc_info:
        BaseDomainRequest(
            username="ACCOUNTDIGIPOS", to="08123456789", trxid=trxid_value
        )
    assert expected_msg in str(exc_info.value)


@pytest.mark.parametrize(
    "username_value",
    [
        "ACCOUNTDIGIPOS",
        "user123",
        "A1B2C3",
        "abcDEF",
        "123456",
        "aSA",
        "Z9ASDA",
        "userUSER123",
    ],
)
def test_base_domain_request_valid_username(username_value: str) -> None:
    req = BaseDomainRequest(
        username=username_value, to="08123456789", trxid="21412LIST"
    )
    assert req.username == username_value


@pytest.mark.parametrize(
    "username_value,expected_msg",
    [
        ("", "Username hanya boleh berisi angka dan huruf (alphanumeric only)"),
        (
            "user name",
            "Username hanya boleh berisi angka dan huruf (alphanumeric only)",
        ),
        (
            "user-name",
            "Username hanya boleh berisi angka dan huruf (alphanumeric only)",
        ),
        (
            "user_name",
            "Username hanya boleh berisi angka dan huruf (alphanumeric only)",
        ),
        ("user@123", "Username hanya boleh berisi angka dan huruf (alphanumeric only)"),
        ("user.123", "Username hanya boleh berisi angka dan huruf (alphanumeric only)"),
        ("user!", "Username hanya boleh berisi angka dan huruf (alphanumeric only)"),
    ],
)
def test_base_domain_request_invalid_username(
    username_value: str, expected_msg: str
) -> None:
    with pytest.raises(ValidationError) as exc_info:
        BaseDomainRequest(username=username_value, to="08123456789", trxid="21412LIST")
    assert expected_msg in str(exc_info.value)
