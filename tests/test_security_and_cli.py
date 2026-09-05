"""
Tests for security fixes and CLI error handling.
"""
import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from agents.base import AuditTrail, PHIGuard
from cli import main


def test_audit_trail_ephemeral_key_warning():
    """AuditTrail should warn when no secret key is provided."""
    # Remove env var if set
    original = os.environ.pop("AUDIT_SECRET_KEY", None)
    try:
        with pytest.warns(RuntimeWarning, match="AUDIT_SECRET_KEY not set"):
            trail = AuditTrail()
        assert trail.secret_key is not None
    finally:
        if original is not None:
            os.environ["AUDIT_SECRET_KEY"] = original


def test_audit_trail_with_env_key():
    """AuditTrail should use AUDIT_SECRET_KEY from environment."""
    os.environ["AUDIT_SECRET_KEY"] = "test-secret-key-123"
    try:
        trail = AuditTrail()
        assert trail.secret_key == b"test-secret-key-123"
    finally:
        os.environ.pop("AUDIT_SECRET_KEY", None)


def test_audit_trail_with_explicit_key():
    """AuditTrail should accept explicit secret key."""
    trail = AuditTrail(secret_key="explicit-key")
    assert trail.secret_key == b"explicit-key"


def test_audit_integrity_still_works():
    """Audit trail integrity verification should still function."""
    trail = AuditTrail(secret_key="test-key")
    trail.log("test", "tier", "event", {"data": "value"})
    trail.log("test", "tier", "event2", {"data": "value2"})
    assert trail.verify_integrity() is True
    assert len(trail.get_trail()) == 2


def test_cli_batch_missing_file():
    """CLI batch should return error code for missing file."""
    result = main(["batch", "-i", "nonexistent_file.csv"])
    assert result == 1


def test_cli_batch_success():
    """CLI batch should process sample.csv successfully."""
    result = main(["batch", "-i", "sample.csv", "-o", "test_output.csv"])
    assert result == 0
    # Clean up
    if os.path.exists("test_output.csv"):
        os.remove("test_output.csv")


def test_phi_redaction():
    """PHIGuard should redact PHI from text."""
    text = "Patient John Doe MRN-123456 test"
    redacted = PHIGuard.redact_phi(text)
    assert "John Doe" not in redacted
    assert "MRN-123456" not in redacted
    assert "[REDACTED_IDENTIFIER]" in redacted
