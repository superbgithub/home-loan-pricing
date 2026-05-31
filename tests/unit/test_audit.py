"""Unit tests for JSON audit logger."""
import hashlib
import json
import sys
from decimal import Decimal
from io import StringIO
from unittest.mock import patch

from src.audit.logger import audit_context, hash_inputs


class TestHashInputs:
    def test_same_data_produces_same_hash(self):
        data = {"home_price": "320000", "rate": "6.5"}
        assert hash_inputs(data) == hash_inputs(data)

    def test_different_data_produces_different_hash(self):
        a = {"rate": "6.5"}
        b = {"rate": "7.0"}
        assert hash_inputs(a) != hash_inputs(b)

    def test_decimal_serialised(self):
        h = hash_inputs({"amount": Decimal("320000.00")})
        assert isinstance(h, str)
        assert len(h) == 64  # SHA-256 hex

    def test_key_order_independent(self):
        a = {"b": 2, "a": 1}
        b = {"a": 1, "b": 2}
        assert hash_inputs(a) == hash_inputs(b)


class TestAuditContext:
    def test_emits_json_line_to_stdout(self, capsys):
        with audit_context("fixed", 1, {"rate": "6.5"}) as _:
            pass
        captured = capsys.readouterr()
        record = json.loads(captured.out.strip())
        assert record["loan_type"] == "fixed"

    def test_record_has_required_fields(self, capsys):
        with audit_context("fixed", 1, {}) as _:
            pass
        record = json.loads(capsys.readouterr().out.strip())
        for field in ("request_id", "timestamp", "loan_type", "scenario_count",
                      "inputs_hash", "outputs_summary", "duration_ms", "error"):
            assert field in record

    def test_error_is_null_on_success(self, capsys):
        with audit_context("fixed", 1, {}) as _:
            pass
        record = json.loads(capsys.readouterr().out.strip())
        assert record["error"] is None

    def test_error_populated_on_exception(self, capsys):
        try:
            with audit_context("fixed", 1, {}) as _:
                raise ValueError("boom")
        except ValueError:
            pass
        record = json.loads(capsys.readouterr().out.strip())
        assert record["error"] == "boom"

    def test_duration_ms_present(self, capsys):
        with audit_context("arm", 1, {}) as _:
            pass
        record = json.loads(capsys.readouterr().out.strip())
        assert isinstance(record["duration_ms"], int)
        assert record["duration_ms"] >= 0

    def test_scenario_count_recorded(self, capsys):
        with audit_context("comparison", 3, {}) as _:
            pass
        record = json.loads(capsys.readouterr().out.strip())
        assert record["scenario_count"] == 3

    def test_outputs_summary_settable(self, capsys):
        with audit_context("fixed", 1, {}) as record:
            record["outputs_summary"] = {"monthly_payment": "2022.62"}
        out = json.loads(capsys.readouterr().out.strip())
        assert out["outputs_summary"]["monthly_payment"] == "2022.62"
