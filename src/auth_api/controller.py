from datetime import datetime

from auth_shared.db import db
from auth_shared.models import DbUser, DbMeteringPointDelegate
from auth_shared.queries import UserQuery, MeteringPointDelegateQuery


class DatabaseController(object):
    """
    Controls business logic for SQL database.
    """

    def get_or_create_user(
            self,
            session: db.Session,
            subject: str,
    ) -> DbUser:
        """
        TODO
        """
        user = UserQuery(session) \
            .has_subject(subject) \
            .one_or_none()

        if user is None:
            user = DbUser(
                subject=subject,
                created=datetime.now(),  # TODO timezone
            )
            session.add(user)

        return user

    def meteringpoint_delegate_exists(
            self,
            session: db.Session,
            subject: str,
            gsrn: str,
    ) -> bool:
        """
        Check whether or not a subject has been delegated access to
        a MeteringPoint.
        """
        return MeteringPointDelegateQuery(session) \
            .has_subject(subject) \
            .has_gsrn(gsrn) \
            .exists()

    def get_or_create_meteringpoint_delegate(
            self,
            session: db.Session,
            subject: str,
            gsrn: str,
    ) -> DbMeteringPointDelegate:
        """
        TODO
        """
        delegate = MeteringPointDelegateQuery(session) \
            .has_subject(subject) \
            .has_gsrn(gsrn) \
            .one_or_none()

        if delegate is None:
            delegate = DbMeteringPointDelegate(
                subject=subject,
                gsrn=gsrn,
            )
            session.add(delegate)

        return delegate

    def delete_meteringpoint_delegate(
            self,
            session: db.Session,
            subject: str,
            gsrn: str,
    ):
        """
        TODO
        """
        MeteringPointDelegateQuery(session) \
            .has_subject(subject) \
            .has_gsrn(gsrn) \
            .delete()


# -- Singletons --------------------------------------------------------------


controller = DatabaseController()
