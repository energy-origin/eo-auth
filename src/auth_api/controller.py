# from datetime import datetime
#
# from .db import db
# from .models import DbUser
# from .queries import UserQuery
#
#
# class DatabaseController(object):
#     """
#     Controls business logic for SQL database.
#     """
#
#     # def is_current_owner(
#     #         self,
#     #         session: db.Session,
#     #         subject: str,
#     #         gsrn: str,
#     # ) -> bool:
#     #     """
#     #     Check if subject is the current owner of a MeteringPoint.
#     #
#     #     :param session:
#     #     :param subject:
#     #     :param gsrn:
#     #     :return:
#     #     """
#     #     query = MeteringPointOwnerQuery(session) \
#     #         .has_subject(subject) \
#     #         .has_gsrn(gsrn) \
#     #         .is_current_owner()
#     #
#     #     # Checking the exact result count enforces that maximum
#     #     # one owner can exists for a given MeteringPoint
#     #     return query.count() == 1
#
#     def get_or_create_user(
#             self,
#             session: db.Session,
#             subject: str,
#     ) -> DbUser:
#         """
#         TODO
#         """
#         user = UserQuery(session) \
#             .has_subject(subject) \
#             .one_or_none()
#
#         if user is None:
#             user = DbUser(
#                 subject=subject,
#                 created=datetime.now(),  # TODO timezone
#             )
#             session.add(user)
#
#         return user
#
#     # def meteringpoint_delegate_exists(
#     #         self,
#     #         session: db.Session,
#     #         subject: str,
#     #         gsrn: str,
#     # ) -> bool:
#     #     """
#     #     Check whether or not a subject has been delegated access to
#     #     a MeteringPoint.
#     #     """
#     #     return MeteringPointDelegateQuery(session) \
#     #         .has_subject(subject) \
#     #         .has_gsrn(gsrn) \
#     #         .exists()
#     #
#     # def get_or_create_meteringpoint_delegate(
#     #         self,
#     #         session: db.Session,
#     #         subject: str,
#     #         gsrn: str,
#     # ) -> DbMeteringPointDelegate:
#     #     """
#     #     TODO
#     #     """
#     #     delegate = MeteringPointDelegateQuery(session) \
#     #         .has_subject(subject) \
#     #         .has_gsrn(gsrn) \
#     #         .one_or_none()
#     #
#     #     if delegate is None:
#     #         delegate = DbMeteringPointDelegate(
#     #             subject=subject,
#     #             gsrn=gsrn,
#     #         )
#     #         session.add(delegate)
#     #
#     #     return delegate
#
#     def delete_meteringpoint_delegate(
#             self,
#             session: db.Session,
#             subject: str,
#             gsrn: str,
#     ):
#         """
#         TODO
#         """
#         MeteringPointDelegateQuery(session) \
#             .has_subject(subject) \
#             .has_gsrn(gsrn) \
#             .delete()
#
#     # def is_owner
#
#
# # -- Singletons --------------------------------------------------------------
#
#
# controller = DatabaseController()
