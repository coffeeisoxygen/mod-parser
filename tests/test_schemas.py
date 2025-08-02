import pytest
from pydantic import ValidationError
from src.schemas import TrimRequest


def test_trim_request_required_fields():
    data = {"end": "list_paket", "to": "08123456789", "trxid": "TRX123LIST"}
    req = TrimRequest(**data)
    assert req.end == "list_paket"
    assert req.to == "08123456789"
    assert req.trxid == "TRX123LIST"


def test_trim_request_extra_fields_allowed():
    data = {
        "end": "list_paket",
        "to": "08123456789",
        "trxid": "TRX123LIST",
        "extra_field": "extra_value",
    }
    req = TrimRequest(**data)
    assert req.end == "list_paket"
    assert req.to == "08123456789"
    assert req.trxid == "TRX123LIST"
    # Access extra field robustly
    assert getattr(req, "extra_field", None) == "extra_value" or (
        hasattr(req, "model_extra") and req.model_extra["extra_field"] == "extra_value" # type: ignore
    )


@pytest.mark.parametrize("missing_field", ["end", "to", "trxid"])
def test_trim_request_missing_required_fields(missing_field):
    data = {"end": "list_paket", "to": "08123456789", "trxid": "TRX123LIST"}
    data.pop(missing_field)
    with pytest.raises(ValidationError):
        TrimRequest(**data)
