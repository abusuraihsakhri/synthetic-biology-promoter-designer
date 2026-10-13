"""Security and CSV regression coverage."""
import csv
import json
import pytest
from pydantic import ValidationError

from agents.base import AuditTrail, SecurityException
from agents.models import SystemTaskPayload, UrgencyLevel
from agents.supervisor import SystemSupervisor
from cli import main as cli_main
from synbio_promoter.cli import main as alternate_main
from csv_utils import parse_csv_boolean


def test_audit_detects_signature_tampering():
    trail = AuditTrail(secret_key="controlled-test-key")
    trail.log("supervisor", "tier", "event", {"test": 1})
    trail.log("supervisor", "tier", "event2", {"test": 2})
    assert trail.verify_integrity()
    trail.logs[0]["actor"] = "tampered"
    assert not trail.verify_integrity()


def test_audit_detects_changed_signature_and_missing_field():
    trail = AuditTrail(secret_key="controlled-test-key")
    trail.log("supervisor", "tier", "event", {})
    trail.logs[0]["current_hash"] = "0" * 64
    assert not trail.verify_integrity()
    del trail.logs[0]["current_hash"]
    assert not trail.verify_integrity()


def test_audit_snapshot_is_not_mutable():
    trail = AuditTrail(secret_key="controlled-test-key")
    trail.log("supervisor", "tier", "event", {})
    trail.get_trail()[0]["actor"] = "changed"
    assert trail.verify_integrity()
    assert trail.get_trail()[0]["actor"] == "supervisor"


def test_reject_nonfinite_input():
    for value in [float("nan"), float("inf"), float("-inf")]:
        with pytest.raises(ValidationError):
            SystemTaskPayload(task_id="T1", target_identifier="KEY-01", primary_metric=value)


def test_reject_phi_hidden_in_attributes():
    service = SystemSupervisor()
    payload = SystemTaskPayload(
        task_id="T1", target_identifier="KEY-01", primary_metric=1,
        attributes={"raw": "Patient MRN-994827"}
    )
    with pytest.raises(SecurityException):
        service.process_task(payload)


@pytest.mark.parametrize("value,expected", [("True", True), ("False", False), ("0", False), ("yes", True), ("", False)])
def test_csv_boolean(value, expected):
    assert parse_csv_boolean(value) is expected


@pytest.mark.parametrize("entrypoint", [cli_main, alternate_main])
def test_csv_false_does_not_escalate(tmp_path, entrypoint):
    input_path = tmp_path / "input.csv"
    output_path = tmp_path / "output.csv"
    input_path.write_text(
        "task_id,target_identifier,primary_metric,secondary_metric,is_critical_flag,status_descriptor\n"
        "T1,KEY-01,10,1,False,NOMINAL\n", encoding="utf-8"
    )
    assert entrypoint(["batch", "-i", str(input_path), "-o", str(output_path)]) == 0
    row = list(csv.DictReader(output_path.open(encoding="utf-8")))[0]
    assert row.get("overall_urgency", row.get("overall_status")) in {"ROUTINE", "NOMINAL_OPTIMAL"}
    assert row.get("critical_count", "0") == "0"


@pytest.mark.parametrize("entrypoint", [cli_main, alternate_main])
def test_csv_malformed_number_gracefully_fails(tmp_path, entrypoint):
    input_path = tmp_path / "invalid.csv"
    input_path.write_text("task_id,primary_metric\nT1,nan\n", encoding="utf-8")
    assert entrypoint(["batch", "-i", str(input_path), "-o", str(tmp_path / "output.csv")]) == 1
    assert not (tmp_path / "output.csv").exists()


def test_verify_audit_command_reports_failure(monkeypatch):
    from agents.base import AuditLogger
    monkeypatch.setattr(AuditLogger, "verify_integrity", staticmethod(lambda: False))
    assert cli_main(["verify-audit"]) == 1


def test_concurrent_audit_entries_form_valid_chain():
    from concurrent.futures import ThreadPoolExecutor
    trail = AuditTrail(secret_key="controlled-test-key")
    def log_one(i):
        trail.log("worker", "tier", "task", {"i": i})
    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(log_one, range(100)))
    assert len(trail.get_trail()) == 100
    assert trail.verify_integrity()


@pytest.mark.parametrize("entrypoint", [cli_main, alternate_main])
def test_extra_csv_fields_report_error(tmp_path, entrypoint):
    source = tmp_path / "too_many_fields.csv"
    source.write_text("task_id,primary_metric\nT1,10,extra\n", encoding="utf-8")
    assert entrypoint(["batch", "-i", str(source), "-o", str(tmp_path / "out.csv")]) == 1
