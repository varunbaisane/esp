# pyrefly: ignore [missing-import]
import pytest
from unittest.mock import patch, MagicMock

from app.email.models import EmailMessage
from app.email.console_provider import ConsoleProvider
from app.email.smtp_provider import SMTPProvider
from app.email.brevo_provider import BrevoProvider
from app.email.factory import get_email_provider
from app.services.email_service import EmailService
# pyrefly: ignore [missing-import]
from sib_api_v3_sdk.rest import ApiException

def test_email_factory_console(monkeypatch):
    monkeypatch.setattr("app.email.factory.settings.EMAIL_PROVIDER", "console")
    provider = get_email_provider()
    assert isinstance(provider, ConsoleProvider)

def test_email_factory_smtp(monkeypatch):
    monkeypatch.setattr("app.email.factory.settings.EMAIL_PROVIDER", "smtp")
    provider = get_email_provider()
    assert isinstance(provider, SMTPProvider)

def test_email_factory_brevo(monkeypatch):
    monkeypatch.setattr("app.email.factory.settings.EMAIL_PROVIDER", "brevo")
    monkeypatch.setattr("app.email.brevo_provider.settings.BREVO_API_KEY", "test-key")
    provider = get_email_provider()
    assert isinstance(provider, BrevoProvider)

def test_email_factory_unknown(monkeypatch):
    monkeypatch.setattr("app.email.factory.settings.EMAIL_PROVIDER", "unknown")
    with pytest.raises(ValueError, match="Unknown EMAIL_PROVIDER configuration: unknown"):
        get_email_provider()

def test_console_provider_output(capsys):
    provider = ConsoleProvider()
    message = EmailMessage(
        to=["test@example.com"],
        cc=["cc@example.com"],
        bcc=["bcc@example.com"],
        subject="Test Console",
        text="Hello text",
        html="<p>Hello HTML</p>"
    )
    provider.send(message)
    captured = capsys.readouterr()
    
    assert "EMAIL SIMULATION (ConsoleProvider)" in captured.out
    assert "To:      test@example.com" in captured.out
    assert "Cc:      cc@example.com" in captured.out
    assert "Bcc:     bcc@example.com" in captured.out
    assert "Subject: Test Console" in captured.out
    assert "[TEXT BODY]" in captured.out
    assert "Hello text" in captured.out
    assert "[HTML BODY]" in captured.out
    assert "<p>Hello HTML</p>" in captured.out

def test_email_service_delegation():
    mock_provider = MagicMock()
    service = EmailService(provider=mock_provider)
    
    message = EmailMessage(
        to=["delegate@example.com"],
        subject="Delegation test"
    )
    
    service.send(message)
    mock_provider.send.assert_called_once_with(message)

def test_brevo_provider_send(monkeypatch):
    monkeypatch.setattr("app.email.brevo_provider.settings.BREVO_API_KEY", "test-key")
    monkeypatch.setattr("app.email.brevo_provider.settings.EMAIL_FROM_NAME", "Test Name")
    monkeypatch.setattr("app.email.brevo_provider.settings.EMAIL_FROM_ADDRESS", "test@example.com")
    
    provider = BrevoProvider()
    
    # Mock the internal client
    provider.api = MagicMock()
    
    message = EmailMessage(
        to=["recipient@example.com"],
        subject="Test Brevo",
        text="Hello plain text"
    )
    
    provider.send(message)
    
    # Verify the internal client was called with correct payload
    provider.api.send_transac_email.assert_called_once()
    call_args = provider.api.send_transac_email.call_args[0][0]
    
    assert call_args.sender == {"name": "Test Name", "email": "test@example.com"}
    assert call_args.to == [{"email": "recipient@example.com"}]
    assert call_args.subject == "Test Brevo"
    assert call_args.text_content == "Hello plain text"
    assert call_args.html_content is None

def test_brevo_provider_api_exception(monkeypatch):
    
    monkeypatch.setattr("app.email.brevo_provider.settings.BREVO_API_KEY", "test-key")
    provider = BrevoProvider()
    provider.api = MagicMock()
    provider.api.send_transac_email.side_effect = ApiException(status=401, reason="Unauthorized")
    
    message = EmailMessage(
        to=["recipient@example.com"],
        subject="Test Error"
    )
    
    with pytest.raises(RuntimeError, match="Failed to send email via Brevo API:"):
        provider.send(message)
