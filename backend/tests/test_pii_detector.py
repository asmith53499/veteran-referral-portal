from app.core.pii_detector import detect_pii


def test_detects_ssn():
    assert detect_pii("SSN: 123-45-6789") is True


def test_detects_phone_number():
    assert detect_pii("Call me at 555-123-4567") is True


def test_detects_email():
    assert detect_pii("Contact: jane.doe@example.com") is True


def test_detects_full_name():
    assert detect_pii("Patient name: John Smith") is True


def test_does_not_flag_uuid_token():
    assert detect_pii("a1b2c3d4-e5f6-7890-abcd-ef1234567890") is False


def test_does_not_flag_short_codes():
    assert detect_pii("VSA-12") is False
