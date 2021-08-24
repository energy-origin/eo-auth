# from dataclasses import dataclass
#
# from energytt_platform.tokens import TokenEncoder
# from energytt_platform.serialize import Serializable
#
# from auth_api.config import SYSTEM_SECRET
#
#
# @dataclass
# class AuthState(Serializable):
#     redirect_uri: str
#
#
# auth_state_encoder = TokenEncoder(
#     cls=AuthState,
#     secret=SYSTEM_SECRET,
# )
