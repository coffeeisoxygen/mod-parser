import os
from unittest.mock import patch

import pytest
from src.schemas import TrimRequest
from src.service import build_query, forward_request


class DummyTrimRequest(TrimRequest):
    # Optionally extend or mock if needed
    pass


def test_build_query_realistic():
    req = TrimRequest(
        end="list_paket",
        to="08123456789",
        trxid="TRX123LIST",
        **{
            "kolom": "productId,productName",
            "category": "DATA",
            "payment_method": "LINKAJA",
        },
    )
    query = build_query(req)
    assert "end=list_paket" in query
    assert "to=08123456789" in query
    assert "trxid=TRX123LIST" in query
    assert (
        "kolom=productId%2CproductName" in query
        or "kolom=productId,productName" in query
    )
    assert "category=DATA" in query
    assert "payment_method=LINKAJA" in query


def test_build_query_exclude_none():
    req = TrimRequest(end="abc", to="x", trxid="y", **{"kolom": None})
    query = build_query(req)
    assert "kolom" not in query
    assert "end=abc" in query
    assert "to=x" in query
    assert "trxid=y" in query


@patch.dict(os.environ, {"TARGET_BASEURL": "http://example.com"})
def test_forward_request_builds_endpoint():
    req = TrimRequest(
        end="list_paket",
        to="08123456789",
        trxid="TRX123LIST",
        **{"kolom": "productId,productName", "category": "DATA"},
    )
    endpoint = forward_request(req)
    assert endpoint.startswith("http://example.com/list_paket?")
    assert "to=08123456789" in endpoint
    assert "trxid=TRX123LIST" in endpoint
    assert (
        "kolom=productId%2CproductName" in endpoint
        or "kolom=productId,productName" in endpoint
    )


@patch.dict(os.environ, {}, clear=True)
def test_forward_request_missing_baseurl():
    req = TrimRequest(end="fail", to="x", trxid="y")
    with pytest.raises(RuntimeError):
        forward_request(req)
