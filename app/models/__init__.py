import datetime
from uuid import UUID
from uuid import uuid4

from app.extensions import db


class BaseModel(db.Model):
    __abstract__ = True
    id: db.Mapped[UUID] = db.mapped_column(
        primary_key=True,
        default=uuid4
    )
    created: db.Mapped[datetime.datetime] = db.mapped_column(
        db.DateTime,
        default=datetime.datetime.now,
        nullable=False
    )
    updated: db.Mapped[datetime.datetime] = db.mapped_column(
        db.DateTime,
        default=datetime.datetime.now,
        onupdate=datetime.datetime.now,
        nullable=False
    )
