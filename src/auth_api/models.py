import sqlalchemy as sa
from sqlalchemy import func
from sqlalchemy.orm import relationship

from .db import db


class DbUser(db.ModelBase):
    """
    TODO
    """
    __tablename__ = 'user'
    __table_args__ = (
        sa.PrimaryKeyConstraint('subject'),
        sa.UniqueConstraint('subject'),
    )

    subject = sa.Column(sa.String(), index=True, nullable=False)
    created = sa.Column(sa.DateTime(timezone=True), nullable=False, server_default=func.now())

    # Social security number, encrypted
    ssn = sa.Column(sa.String(), index=True, nullable=False)


class DbExternalUser(db.ModelBase):
    """
    Represents a user logging in via some Identity Provider.

    A single user (represented via the DbUser model) can have multiple logins
    using either different Identity Providers, or using different login method
    via the same Identity Provider (for instance, logging in via MitID or
    NemID results in different user IDs even if its the same person).
    """
    __tablename__ = 'user_external'
    __table_args__ = (
        sa.PrimaryKeyConstraint('id'),
    )

    id = sa.Column(sa.Integer(), primary_key=True, index=True)
    created = sa.Column(sa.DateTime(timezone=True), nullable=False, server_default=func.now())
    subject = sa.Column(sa.String(), sa.ForeignKey('user.subject'), index=True, nullable=False)

    # Identity Provider's ID of the user
    external_subject = sa.Column(sa.String(), index=True, nullable=False)

    # Relationships
    user = relationship('DbUser', foreign_keys=[subject], uselist=False)


class DbLoginRecord(db.ModelBase):
    """
    TODO
    """
    __tablename__ = 'login_record'
    __table_args__ = (
        sa.PrimaryKeyConstraint('id'),
    )

    id = sa.Column(sa.Integer(), index=True)
    subject = sa.Column(sa.String(), index=True, nullable=False)
    created = sa.Column(sa.DateTime(timezone=True), nullable=False, server_default=func.now())


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
    issued = sa.Column(sa.DateTime(timezone=True), nullable=False)
    expires = sa.Column(sa.DateTime(timezone=True), nullable=False)
    subject = sa.Column(sa.String(), index=True, nullable=False)
