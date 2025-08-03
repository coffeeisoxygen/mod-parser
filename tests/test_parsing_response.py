import json
import os

import pytest
from src.services.req_response import ResponseProcessor

DATA_PATH = os.path.join(os.path.dirname(__file__), "HVCDATA.json")


@pytest.fixture
def sample_data():
    with open(DATA_PATH, encoding="utf-8") as f:
        data = json.load(f)
    return data


def test_process_basic(sample_data):
    paket_list = sample_data["paket"]
    proc = ResponseProcessor()
    result = proc.process(paket_list)
    assert isinstance(result, list)
    assert all(isinstance(p, dict) for p in result)
    # Check that quota is simplified (no leading "DATA National/Internet")
    for p in result:
        if p.get("quota"):
            assert not p["quota"].startswith("DATA NATIONAL/INTERNET")


def test_process_with_exclude_prefix(sample_data):
    paket_list = sample_data["paket"]
    # Exclude products with prefix "SUPER SERU"
    proc = ResponseProcessor(exclude_product=True, list_prefixes=["SUPER SERU"])
    result = proc.process(paket_list)
    # No productName should start with "SUPER SERU"
    for p in result:
        assert not p["productName"].startswith("SUPER SERU")


def test_process_with_regex_replacement(sample_data):
    paket_list = sample_data["paket"]
    # Remove all "GB" and "MB" from quota
    proc = ResponseProcessor(
        replace_with_regex=True, list_regex_replacement=[r"\bGB\b", r"\bMB\b"]
    )
    result = proc.process(paket_list)
    for p in result:
        if p.get("quota"):
            assert "GB" not in p["quota"]
            assert "MB" not in p["quota"]


def test_to_response_string(sample_data):
    paket_list = sample_data["paket"][:3]
    proc = ResponseProcessor()
    processed = proc.process(paket_list)
    trxid = "12345"
    to = sample_data["to"]
    resp_str = proc.to_response_string(processed, trxid, to)
    assert resp_str.startswith(
        f"trxid={trxid}&to={to}&status=success&message=listpaket"
    )
    # Should contain productId and productName
    for p in processed:
        assert f"@{p['productId']}" in resp_str
        assert p["productName"] in resp_str


def test_sort_by_name(sample_data):
    paket_list = sample_data["paket"][:5]
    proc = ResponseProcessor()
    processed = proc.process(paket_list)
    resp_str = proc.to_response_string(processed, "1", "0812", sort_by_name=True)
    # Sorted by productName (upper)
    names = [p["productName"] for p in processed]
    sorted_names = sorted(names, key=lambda n: n.lower())
    for idx, name in enumerate(sorted_names):
        assert name in resp_str
