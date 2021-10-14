import sqlalchemy as sa
# from datetime import datetime

from .db import db


class DbUser(db.ModelBase):
    """
    Relationship between Signaturgruppen "subject" and encrypted CPR number.
    """
    __tablename__ = 'user'
    __table_args__ = (
        sa.PrimaryKeyConstraint('id'),
    )

    id = sa.Column(sa.Integer(), index=True)
    cpr = sa.Column(sa.String(), index=True, nullable=False)
    created = sa.Column(sa.DateTime(timezone=True), nullable=False)

    # Our own ID of the user
    internal_subject = sa.Column(sa.String(), index=True, nullable=False)

    # Identity Provider's ID of the user
    external_subject = sa.Column(sa.String(), index=True, nullable=False)


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
    created = sa.Column(sa.DateTime(timezone=True), nullable=False)


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
