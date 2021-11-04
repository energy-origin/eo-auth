from typing import Optional
from datetime import datetime
from abc import abstractmethod
from dataclasses import dataclass


@dataclass
class OpenIDConnectToken:
    """
    OpenID Connect ID token
    """

    @property
    @abstractmethod
    def issued(self) -> datetime:
        """
        TODO
        """
        raise NotImplementedError

    @property
    def expires(self) -> datetime:
        """
        Time of expiration.
        """
        raise NotImplementedError

    @property
    def subject(self) -> str:
        """
        User unique subject (ID).
        """
        raise NotImplementedError

    @property
    def provider(self) -> str:
        """
        Name of identity provider.
        """
        raise NotImplementedError

    @property
    def ssn(self) -> Optional[str]:
        """
        Social security number (for privat persons).
        """
        raise NotImplementedError

    @property
    def tin(self) -> Optional[str]:
        """
        Tax identification number (for companies).
        """
        raise NotImplementedError

    @property
    def is_private(self) -> bool:
        """
        Whether or not this is a privat person.
        """
        raise NotImplementedError

    @property
    def is_company(self) -> bool:
        """
        Whether or not this is a company.
        """
        raise NotImplementedError
