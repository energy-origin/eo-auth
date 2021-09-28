from sqlalchemy import orm, func, and_

from energytt_platform.sql import SqlQuery

from .models import DbToken


# class UserQuery(SqlQuery):
#     """
#     Query DbUser.
#     """
#     def _get_base_query(self) -> orm.Query:
#         """
#         TODO
#         """
#         return self.session.query(DbUser)
#
#     def has_subject(self, subject: str) -> 'UserQuery':
#         """
#         TODO
#         """
#         return self.filter(DbUser.subject == subject)


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
