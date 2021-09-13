import sqlalchemy as sa
from datetime import datetime

from sqlalchemy.orm import relationship

from .db import db


class DbUser(db.ModelBase):
    """
    TODO
    """
    __tablename__ = 'users'
    __table_args__ = (
        sa.PrimaryKeyConstraint('subject'),
        sa.UniqueConstraint('subject'),
    )

    subject = sa.Column(sa.String(), index=True, nullable=False)
    created = sa.Column(sa.DateTime(timezone=True), nullable=False)
    last_login = sa.Column(sa.DateTime(timezone=True))

    @property
    def has_logged_in(self) -> bool:
        """
        TODO
        """
        return self.last_login is not None

    def update_last_login(self):
        """
        TODO
        """
        self.last_login = datetime.now()


class DbToken(db.ModelBase):
    """
    TODO
    """
    __tablename__ = 'token'
    __table_args__ = (
        sa.PrimaryKeyConstraint('opaque_token'),
        sa.UniqueConstraint('opaque_token'),
        sa.CheckConstraint('issued < expires'),
    )

    opaque_token = sa.Column(sa.String(), index=True, nullable=False)
    internal_token = sa.Column(sa.String(), nullable=False)
    # subject = sa.Column(sa.ForeignKey('users.subject'), index=True, nullable=False)
    subject = sa.Column(sa.String(), index=True, nullable=False)
    issued = sa.Column(sa.DateTime(timezone=True), nullable=False)
    expires = sa.Column(sa.DateTime(timezone=True), nullable=False)

    # user = relationship('DbUser', foreign_keys=[subject])


class DbMeteringPointOwner(db.ModelBase):
    """
    TODO
    """
    __tablename__ = 'meteringpoint_owner'
    __table_args__ = (
        sa.PrimaryKeyConstraint('id'),
        # sa.CheckConstraint('end IS NULL OR begin < end'),
    )

    id = sa.Column(sa.Integer(), index=True)
    # subject = sa.Column(sa.ForeignKey('users.subject'), index=True, nullable=False)
    subject = sa.Column(sa.String(), index=True, nullable=False)
    gsrn = sa.Column(sa.String(), index=True, nullable=False)
    begin = sa.Column(sa.DateTime(timezone=True), index=True, nullable=False)
    end = sa.Column(sa.DateTime(timezone=True), index=True)

    # user = relationship('DbUser', foreign_keys=[subject])

    def set_begins_now(self):
        """
        TODO
        """
        self.begin = sa.func.now()

    def set_ends_now(self):
        """
        TODO
        """
        self.end = sa.func.now()


class DbMeteringPointDelegate(db.ModelBase):
    """
    TODO
    """
    __tablename__ = 'meteringpoint_delegate'
    __table_args__ = (
        sa.PrimaryKeyConstraint('gsrn', 'subject'),
        sa.UniqueConstraint('gsrn', 'subject'),
    )

    # subject = sa.Column(sa.ForeignKey('users.subject'), index=True, nullable=False)
    subject = sa.Column(sa.String(), index=True, nullable=False)
    gsrn = sa.Column(sa.String(), index=True, nullable=False)

    # user = relationship('DbUser', foreign_keys=[subject])
