from abc import ABC, abstractmethod
from typing import Optional


class LDAPService(ABC):

    @abstractmethod
    def authenticate(self, username: str, password: str) -> Optional[dict]:
        """
        Authenticate a user against LDAP.
        Returns a dict of user attributes on success, or None on failure.
        """
        pass