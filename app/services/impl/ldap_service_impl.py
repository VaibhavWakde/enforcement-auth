import ssl
import logging
from typing import Optional, List, Dict, Any

from ldap3 import Server, Connection, ALL, SUBTREE, Tls, SIMPLE

from app.config.ldap_config import settings
from app.services.interfaces.ldap_service import LDAPService

logger = logging.getLogger(__name__)


class LDAPServiceImpl(LDAPService):
    """
    Unified LDAP authentication provider supporting both local OpenLDAP
    and organization Active Directory / LDAP servers based on configuration.
    """

    def __init__(self):
        # Resolve config based on active LDAP environment
        if settings.USE_ORG_LDAP:
            self.uri = settings.ORG_LDAP_URI
            self.base_dn = settings.ORG_LDAP_BASE_DN
            self.bind_dn = settings.ORG_LDAP_BIND_DN
            self.bind_password = settings.ORG_LDAP_BIND_PASSWORD
            self.user_base = settings.ORG_LDAP_USER_BASE
            self.timeout = settings.ORG_LDAP_TIMEOUT
        else:
            self.uri = settings.LOCAL_LDAP_URI
            self.base_dn = settings.LOCAL_LDAP_BASE_DN
            self.bind_dn = settings.LOCAL_LDAP_BIND_DN
            self.bind_password = settings.LOCAL_LDAP_BIND_PASSWORD
            self.user_base = settings.LOCAL_LDAP_USER_BASE
            self.timeout = settings.LOCAL_LDAP_TIMEOUT

    def _get_server(self) -> Server:
        """
        Creates and returns an ldap3 Server instance with TLS and timeout.
        """
        use_ssl = self.uri.lower().startswith("ldaps://")
        tls = None
        if use_ssl:
            tls = Tls(validate=ssl.CERT_NONE)

        return Server(
            self.uri,
            use_ssl=use_ssl,
            tls=tls,
            get_info=ALL,
            connect_timeout=self.timeout
        )

    def authenticate(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate user credentials against the configured LDAP provider.
        """
        if not username or not password:
            logger.warning("Authentication failed: Username or password is empty")
            return None

        server = self._get_server()

        try:
            logger.info("Attempting manager bind to search for user %s on %s", username, self.uri)
            with Connection(
                server,
                user=self.bind_dn,
                password=self.bind_password,
                authentication=SIMPLE,
                auto_bind=True,
                receive_timeout=self.timeout
            ) as conn:
                
                search_base = f"{self.user_base},{self.base_dn}" if self.user_base else self.base_dn
                
                if settings.USE_ORG_LDAP:
                    search_filter = f"(|(sAMAccountName={username})(mail={username}))"
                    attributes = ["sAMAccountName", "mail", "displayName", "givenName", "sn", "telephoneNumber", "memberOf"]
                else:
                    search_filter = f"(|(uid={username})(mail={username}))"
                    attributes = ["uid", "mail", "cn", "sn", "telephoneNumber", "ou"]

                logger.debug("LDAP search: base=%s, filter=%s", search_base, search_filter)
                conn.search(
                    search_base=search_base,
                    search_filter=search_filter,
                    search_scope=SUBTREE,
                    attributes=attributes
                )

                if not conn.entries:
                    logger.warning("LDAP user not found: %s", username)
                    return None

                user_entry = conn.entries[0]
                user_dn = user_entry.entry_dn
                logger.debug("Found user DN: %s", user_dn)

                user_attrs = self._parse_attributes(user_entry)

            logger.info("Attempting user bind for DN: %s", user_dn)
            with Connection(
                server,
                user=user_dn,
                password=password,
                authentication=SIMPLE,
                auto_bind=True,
                receive_timeout=self.timeout
            ) as user_conn:
                logger.info("LDAP Authentication successful for user: %s", username)
                return user_attrs

        except Exception as e:
            logger.error("LDAP authentication failed due to exception: %s", str(e), exc_info=True)
            return None

    def _parse_attributes(self, entry: Any) -> Dict[str, Any]:
        """
        Extract LDAP attributes and map to unified schema.
        """
        attrs = entry.entry_attributes_as_dict

        def get_first(key: str, default: Any = None) -> Any:
            val = attrs.get(key)
            return val[0] if val else default

        if settings.USE_ORG_LDAP:
            username = get_first("sAMAccountName") or entry.entry_dn
            email = get_first("mail")
            display_name = get_first("displayName", "")
            given_name = get_first("givenName", "")
            sn = get_first("sn", "")

            if given_name:
                first_name = given_name
                last_name = sn if sn else None
            elif display_name:
                parts = display_name.split(maxsplit=1)
                first_name = parts[0]
                last_name = parts[1] if len(parts) > 1 else None
            else:
                first_name = username
                last_name = None

            phone_number = get_first("telephoneNumber")
            member_of = attrs.get("memberOf", [])
            groups = self._parse_groups_from_memberof(member_of)
        else:
            username = get_first("uid") or entry.entry_dn
            email = get_first("mail") or f"{username}@local.dev"
            cn = get_first("cn", "")
            sn = get_first("sn", "")
            
            first_name = cn if cn else username
            last_name = sn if sn else None
            phone_number = get_first("telephoneNumber")
            groups = attrs.get("ou", [])

        return {
            "username": username,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "phone_number": phone_number,
            "groups": groups
        }

    def _parse_groups_from_memberof(self, member_of_list: Any) -> List[str]:
        """
        Helper method to parse Group names from list of group DNs (e.g. memberOf list).
        """
        groups: List[str] = []
        if not member_of_list:
            return groups

        if isinstance(member_of_list, str):
            member_of_list = [member_of_list]

        for dn in member_of_list:
            try:
                parts = dn.split(",")
                for part in parts:
                    if part.strip().upper().startswith("CN="):
                        groups.append(part.split("=")[1].strip())
                        break
            except Exception as e:
                logger.debug("Failed parsing group DN '%s': %s", dn, str(e))
        return groups
