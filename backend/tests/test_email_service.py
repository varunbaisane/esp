# pyrefly: ignore [missing-import]
import pytest
from unittest.mock import patch, MagicMock

from app.email.models import EmailMessage
from app.email.console_provider import ConsoleProvider
from app.email.smtp_provider import SMTPProvider
from app.email.factory import get_email_provider
from app.services.email_service import EmailService

def test_email_factory_console(monkeypatch):
    monkeypatch.setattr("app.email.factory.settings.EMAIL_PROVIDER", "console")
    provider = get_email_provider()
    assert isinstance(provider, ConsoleProvider)

def test_email_factory_smtp(monkeypatch):
    monkeypatch.setattr("app.email.factory.settings.EMAIL_PROVIDER", "smtp")
    provider = get_email_provider()
    assert isinstance(provider, SMTPProvider)

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
