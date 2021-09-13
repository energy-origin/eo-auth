from sqlalchemy import orm, func, and_, or_

from energytt_platform.sql import SqlQuery

from .models import (
    DbUser,
    DbToken,
    DbMeteringPointOwner,
    DbMeteringPointDelegate,
)


class UserQuery(SqlQuery):
    """
    Query DbUser.
    """
    def _get_base_query(self) -> orm.Query:
        """
        TODO
        """
        return self.session.query(DbUser)

    def has_subject(self, subject: str) -> 'UserQuery':
        """
        TODO
        """
        return self.filter(DbUser.subject == subject)


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


class MeteringPointOwnerQuery(SqlQuery):
    """
    Query DbMeteringPointOwner.
    """
    def _get_base_query(self) -> orm.Query:
        """
        TODO
        """
        return self.session.query(DbMeteringPointOwner)

    def has_subject(self, subject: str) -> 'MeteringPointOwnerQuery':
        """
        TODO
        """
        return self.filter(DbMeteringPointOwner.subject == subject)

    def has_gsrn(self, gsrn: str) -> 'MeteringPointOwnerQuery':
        """
        TODO
        """
        return self.filter(DbMeteringPointOwner.gsrn == gsrn)

    def is_current_owner(self) -> 'MeteringPointOwnerQuery':
        """
        TODO
        """
        return self.filter(
            and_(
                DbMeteringPointOwner.begin <= func.now(),
                or_(
                    DbMeteringPointOwner.end > func.now(),
                    DbMeteringPointOwner.end.is_(None),
                ),
            )
        )


class MeteringPointDelegateQuery(SqlQuery):
    """
    Query DbMeteringPointDelegate.
    """
    def _get_base_query(self) -> orm.Query:
        """
        TODO
        """
        return self.session.query(DbMeteringPointDelegate)

    def has_subject(self, subject: str) -> 'MeteringPointDelegateQuery':
        """
        TODO
        """
        return self.filter(DbMeteringPointDelegate.subject == subject)

    def has_gsrn(self, gsrn: str) -> 'MeteringPointDelegateQuery':
        """
        TODO
        """
        return self.filter(DbMeteringPointDelegate.gsrn == gsrn)
