# import uuid
# from typing import Optional
# from dataclasses import dataclass, field
#
# from energytt_platform.bus import topics as t, messages as m
# from energytt_platform.api import Endpoint, Context, Unauthorized
#
# from auth_api.bus import broker
#
#
# class OnboardUser(Endpoint):
#     """
#     Onboards a mocked used for testing.
#     """
#
#     @dataclass
#     class Request:
#         name: str
#         subject: Optional[str] = field(default_factory=uuid.uuid4)
#
#     @dataclass
#     class Response:
#         success: bool
#
#     def handle_request(self, request: Request) -> Response:
#         """
#         Handle HTTP request.
#         """
#         broker.publish(
#             topic=t.AUTH,
#             msg=m.UserOnboarded(
#                 subject=request.subject,
#                 name=request.name,
#             ),
#         )
#
#         return self.Response(success=True)
#
#
# class DemoEndpoint(Endpoint):
#     """
#     Demo endpoint accesses opaque token.
#     """
#
#     @dataclass
#     class Response:
#         success: bool
#         subject: Optional[str]
#
#     def handle_request(self, context: Context) -> Response:
#         """
#         Handle HTTP request.
#         """
#         return self.Response(
#             success=context.token is not None,
#             subject=context.token.subject if context.token else None,
#         )
#
#
# class HealthCheck(Endpoint):
#     """
#     Health check endpoint. Always returns status 200.
#     """
#     def handle_request(self):
#         pass
