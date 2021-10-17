from sqlalchemy import orm, func, and_

from energytt_platform.sql import SqlQuery

from .models import DbUser, DbExternalUser, DbToken


class UserQuery(SqlQuery):
    """
    Query DbUser.
    """
    def _get_base_query(self) -> orm.Query:
        """
        TODO
        """
        return self.session.query(DbUser)

    # def has_opaque_token(self, opaque_token: str) -> 'UserQuery':
    #     """
    #     TODO
    #     """
    #     return self.filter(DbToken.opaque_token == opaque_token)

    # def has_internal_subject2(self, subject: str) -> 'UserQuery':
    #     """
    #     TODO
    #     """
    #     return self.filter(DbUser.internal_subject == subject)

    def has_external_subject(self, subject: str) -> 'UserQuery':
        """
        TODO
        """
        q = self.q \
            .join(DbExternalUser, DbExternalUser.subject == DbUser.subject) \
            .filter(DbExternalUser.external_subject == subject)

        return self.__class__(
            session=self.session,
            q=q,
        )

    # def has_external_subject(self, subject: str) -> 'UserQuery':
    #     """
    #     TODO
    #     """
    #     return self.filter(DbUser.external_subject == subject)

    def has_ssn(self, ssn: str) -> 'UserQuery':
        """
        :param ssn: Social security number, encrypted
        """
        return self.filter(DbUser.ssn == ssn)


class TokenQuery(SqlQuery):
    """
    Query DbToken.
    """
    def _get_base_query(self) -> orm.Query:
        """
        TODO
        """
        return self.session.query(DbToken)

    def has_opaque_token(self, opaque_token: str) -> 'TokenQuery':
        """
        TODO
        """
        return self.filter(DbToken.opaque_token == opaque_token)

    def is_valid(self) -> 'TokenQuery':
        """
        TODO
        """
        return self.filter(and_(
            DbToken.issued <= func.now(),
            DbToken.expires > func.now(),
        ))
