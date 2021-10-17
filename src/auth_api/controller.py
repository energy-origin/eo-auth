from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from .db import db
from .models import DbUser, DbExternalUser
from .queries import UserQuery


class DatabaseController(object):
    """
    Controls business logic for SQL database.
    """

    def get_user_by_external_subject(
            self,
            session: db.Session,
            external_subject: str,
    ) -> Optional[DbUser]:
        """
        TODO

        :param session: Database session
        :param external_subject: Identity Provider's subject
        """
        return UserQuery(session) \
            .has_external_subject(external_subject) \
            .one_or_none()

    def get_user_by_ssn(
            self,
            session: db.Session,
            ssn: str,
    ) -> Optional[DbUser]:
        """
        TODO

        :param session: Database session
        :param ssn: Social security number, unencrypted
        """
        return UserQuery(session) \
            .has_ssn(ssn) \
            .one_or_none()

    def attach_ssn_to_user(
            self,
            session: db.Session,
            external_subject: str,
            ssn: str,
    ) -> DbUser:
        """
        Attaches Social security number to a user.

        Optionally creates the user if it doesn't exists.

        :param session: Database session
        :param external_subject: Identity Provider's subject
        :param ssn: Social security number, unencrypted
        """
        user = self.get_user_by_ssn(
            session=session,
            ssn=ssn,
        )

        if user is None:
            user = self.create_user(
                session=session,
                external_subject=external_subject,
                ssn=ssn,
            )

        return user

    def create_user(
            self,
            session: db.Session,
            external_subject: str,
            ssn: str,
    ) -> DbUser:
        """
        Attaches Social security number to a user.

        Optionally creates the user if it doesn't exists.

        :param session: Database session
        :param external_subject: Identity Provider's subject
        :param ssn: Social security number, unencrypted
        """
        user = DbUser(
            subject=str(uuid4()),
            ssn=ssn,  # TODO encrypt
        )

        external_user = DbExternalUser(
            user=user,
            external_subject=external_subject,
        )

        session.add(user)
        session.add(external_user)

        return user


def encrypt_ssn(ssn: str) -> str:
    pass


def decrypt_ssn(ssn_encrypted: str) -> str:
    pass


# -- Singletons --------------------------------------------------------------


controller = DatabaseController()
