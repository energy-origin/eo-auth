from authlib.jose import jwt
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

from ..models import OpenIDConnectToken


class SignaturgruppenToken(OpenIDConnectToken, Dict[str, Any]):

    @classmethod
    def from_raw_token(
            cls,
            raw_token: Dict[str, Any],
            jwk: str,
    ) -> 'SignaturgruppenToken':
        """
        TODO
        """
        token = cls(raw_token)

        # Decode id_token and override encoded value
        token['id_token_encoded'] = token['id_token']
        token['id_token'] = jwt.decode(token['id_token'], key=jwk)

        # Decode userinfo_token and override encoded value
        token['userinfo_token'] = jwt.decode(token['userinfo_token'], key=jwk)

        return token

    @property
    def issued(self) -> datetime:
        return datetime.fromtimestamp(
            self['id_token']['iat'], tz=timezone.utc)

    @property
    def expires(self) -> datetime:
        return datetime.fromtimestamp(
            self['id_token']['exp'], tz=timezone.utc)

    @property
    def subject(self) -> str:
        return self['id_token']['sub']

    @property
    def provider(self) -> str:
        return self['id_token']['idp']

    @property
    def scope(self) -> List[str]:
        return [s for s in self['scope'].split(' ') if s.strip()]

    @property
    def id_token(self) -> str:
        return self['id_token_encoded']

    @property
    def is_private(self) -> bool:
        return self['userinfo_token']['identity_type'] == 'private'

    @property
    def is_company(self) -> bool:
        return self['userinfo_token']['identity_type'] == 'professional'

    @property
    def ssn(self) -> Optional[str]:
        return self['userinfo_token'].get('dk.cpr')

    @property
    def tin(self) -> Optional[str]:
        return self['userinfo_token'].get('nemid.cvr')
