import logging

from app.config.ldap_config import settings
from app.services.interfaces.email_service import EmailService
from app.services.impl.local_email_service import LocalEmailService
from app.services.impl.splitter_email_service import SplitterEmailService

logger = logging.getLogger(__name__)


class EmailServiceFactory:
    """
    Factory class to dynamically instantiate the appropriate EmailService
    based on environment configurations.
    """

    @staticmethod
    def get_service() -> EmailService:
        if settings.USE_ORG_EMAIL_SERVICE:
            logger.info("EmailServiceFactory: Resolving SplitterEmailService (USE_ORG_EMAIL_SERVICE is True)")
            return SplitterEmailService()
        
        logger.info("EmailServiceFactory: Resolving LocalEmailService (USE_ORG_EMAIL_SERVICE is False)")
        return LocalEmailService()
