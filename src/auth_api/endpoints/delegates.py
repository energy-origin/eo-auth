from typing import List
from dataclasses import dataclass, field

from energytt_platform.api import Endpoint, Context
from energytt_platform.bus import messages as m, topics as t
from energytt_platform.models.auth import MeteringPointDelegate

from auth_shared.db import db
from auth_shared.bus import broker
from auth_shared.queries import (
    MeteringPointOwnerQuery,
    MeteringPointDelegateQuery,
)

from ..controller import controller


class GetMeteringPointDelegateList(Endpoint):
    """
    TODO
    """

    @dataclass
    class Request:
        gsrn: str

    @dataclass
    class Response:
        success: bool
        delegates: List[MeteringPointDelegate] = field(default_factory=list)

    @db.atomic()
    def handle_request(
            self,
            request: Request,
            context: Context,
            session: db.Session,
    ) -> Response:
        """
        TODO
        """
        allowed = MeteringPointOwnerQuery(session) \
            .has_subject(context.token.subject) \
            .has_gsrn(request.gsrn) \
            .is_current_owner() \
            .exists()

        if not allowed:
            # TODO Raise 403 Forbidden
            return self.Response(success=False)

        delegates = MeteringPointDelegateQuery(session) \
            .has_gsrn(request.gsrn) \
            .all()

        return self.Response(
            success=True,
            delegates=delegates,
        )


class GrantMeteringPointDelegate(Endpoint):
    """
    Grants MeteringPointDelegate to a subject.
    """

    @dataclass
    class Request:
        subject: str
        gsrn: str

    @dataclass
    class Response:
        success: bool

    @db.atomic()
    def handle_request(
            self,
            request: Request,
            context: Context,
            session: db.Session,
    ) -> Response:
        """
        TODO

        1) Insert DbMeteringPointDelegate into database
        2) Publish MeteringPointDelegateGranted message to bus

        :param request:
        :param context:
        :param session:
        :return:
        """
        allowed = MeteringPointOwnerQuery(session) \
            .has_subject(context.token.subject) \
            .has_gsrn(request.gsrn) \
            .is_current_owner() \
            .exists()

        # allowed = controller.meteringpoint_delegate_exists(
        #     subject=context.token.subject,
        #     gsrn=request.gsrn,
        # )

        if not allowed:
            # TODO Raise 403 Forbidden
            return self.Response(success=False)

        # TODO Handle atomically:

        # Create delegate (if it doesn't already exist)
        controller.get_or_create_meteringpoint_delegate(
            session=session,
            subject=request.subject,
            gsrn=request.gsrn,
        )

        # Publish to Message Bus
        broker.publish(
            topic=t.AUTH,
            msg=m.MeteringPointDelegateGranted(
                delegate=MeteringPointDelegate(
                    subject=request.subject,
                    gsrn=request.gsrn,
                )
            )
        )

        return self.Response(success=True)


# class GrantMeteringPointDelegate(Endpoint):
#     """
#     Grants MeteringPointDelegate to a subject.
#     """
#
#     @dataclass
#     class Request:
#         subject: str
#         gsrn: str
#
#     @dataclass
#     class Response:
#         success: bool
#
#     @db.atomic()
#     def handle_request(
#             self,
#             request: Request,
#             context: Context,
#             session: db.Session,
#     ) -> Response:
#         """
#         TODO
#
#         1) Insert DbMeteringPointDelegate into database
#         2) Publish MeteringPointDelegateGranted message to bus
#
#         :param request:
#         :param context:
#         :param session:
#         :return:
#         """
#         allowed = controller.meteringpoint_delegate_exists(
#             subject=context.token.subject,
#             gsrn=request.gsrn,
#         )
#
#         if not allowed:
#             # TODO Raise 403 Forbidden
#             return self.Response(success=False)
#
#         # TODO Handle atomically:
#
#         # Create delegate (if it doesn't already exist)
#         controller.get_or_create_meteringpoint_delegate(
#             session=session,
#             subject=request.subject,
#             gsrn=request.gsrn,
#         )
#
#         # Publish to Message Bus
#         broker.publish(
#             topic=t.AUTH,
#             msg=m.MeteringPointDelegateGranted(
#                 delegate=MeteringPointDelegate(
#                     subject=request.subject,
#                     gsrn=request.gsrn,
#                 )
#             )
#         )
#
#         return self.Response(success=True)


class RevokeMeteringPointDelegate(Endpoint):
    """
    Revokes an existing MeteringPointDelegate.
    """

    @dataclass
    class Request:
        subject: str
        gsrn: str

    @dataclass
    class Response:
        success: bool

    @db.atomic()
    def handle_request(
            self,
            request: Request,
            context: Context,
            session: db.Session,
    ) -> Response:
        """
        TODO

        1) Delete DbMeteringPointDelegate from database
        2) Publish MeteringPointDelegateRevoked message to bus

        :param request:
        :param context:
        :param session:
        :return:
        """
        allowed = controller.meteringpoint_delegate_exists(
            subject=context.token.subject,
            gsrn=request.gsrn,
        )

        if not allowed:
            # TODO Raise 403 Forbidden
            return self.Response(success=False)

        if context.token.subject == request.subject:
            # Can not revoke your own delegated access
            # TODO Raise 400 Forbidden
            return self.Response(success=False)

        # TODO Handle atomically:

        # Delete delegate (if it exist)
        controller.delete_meteringpoint_delegate(
            session=session,
            subject=request.subject,
            gsrn=request.gsrn,
        )

        # Publish to Message Bus
        broker.publish(
            topic=t.AUTH,
            msg=m.MeteringPointDelegateRevoked(
                delegate=MeteringPointDelegate(
                    subject=request.subject,
                    gsrn=request.gsrn,
                )
            )
        )

        return self.Response(success=True)
