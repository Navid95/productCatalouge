import datetime
from uuid import UUID
from uuid import uuid4

from marshmallow import post_load
from sqlalchemy import select

from app.extensions import db
from app.extensions import ma


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
    active: db.Mapped[bool] = db.mapped_column(
        default=True,
        index=True
    )

    # NODO 1000: add setters to prevent updating of id, created, updated

    @classmethod
    def read(cls, id: UUID):
        model_object = db.session.scalar(select(cls).where(cls.id == id).where(cls.active == True))
        if not model_object:
            return None
        return model_object

    @classmethod
    def create(cls, model_object):
        if not isinstance(model_object, cls):
            return None
        try:
            db.session.add(model_object)
            db.session.commit()
        except BaseException as e:
            print(e)
            return None
        return model_object

    @classmethod
    def delete(cls, id: UUID):
        model_object, code = cls.read(id)
        if not model_object:
            return False
        model_object.active = False
        try:
            db.session.add(model_object)
            db.session.commit()
            return True
        except BaseException as e:
            print(e)

    @classmethod
    def update(cls, id: UUID, **kwargs):
        model_object = cls.read(id)
        if not model_object:
            return None
        for key, value in kwargs.items():
            try:
                if not hasattr(model_object, key):
                    return None
                setattr(model_object, key, value)
            except BaseException as e:
                print(e)
                return None
            try:
                db.session.add(model_object)
                db.session.commit()
                return model_object
            except BaseException as e:
                print(e)
                return None


class BaseSchema(ma.SQLAlchemyAutoSchema):

    @post_load
    def make_user(self, data, **kwargs):
        return self.Meta.model(**data)
