from abc import ABC, abstractmethod
from app.email.models import EmailMessage

class BaseEmailProvider(ABC):
    @abstractmethod
    def send(self, message: EmailMessage) -> None:
        """
        Send an email message using this provider.
        """
        pass
