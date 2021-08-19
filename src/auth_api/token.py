import jwt
from dataclasses import dataclass

from energytt_platform.serialize import Serializable, simple_serializer

from .config import SERVICE_SECRET


@dataclass
class CallbackToken(Serializable):
    redirect_uri: str


def encode_auth_token(token: CallbackToken) -> str:
    return jwt.encode(
        payload=simple_serializer.serialize(token),
        key=SERVICE_SECRET,
        algorithm='HS256',
    )


def decode_auth_token(encoded_jwt: str) -> CallbackToken:
    payload = jwt.decode(
        jwt=encoded_jwt,
        key=SERVICE_SECRET,
        algorithms=['HS256'],
    )

    return simple_serializer.deserialize(
        data=payload,
        cls=CallbackToken,
    )
