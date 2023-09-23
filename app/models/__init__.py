from datetime import datetime
from uuid import UUID
from uuid import uuid4

from marshmallow import post_load
from sqlalchemy import select
from sqlalchemy import inspect

from app.extensions import db
from app.extensions import ma


class BaseModel(db.Model):
    __abstract__ = True
    id: db.Mapped[UUID] = db.mapped_column(
        primary_key=True,
        default=uuid4
    )
    created: db.Mapped[datetime] = db.mapped_column(
        db.DateTime,
        default=datetime.now,
        nullable=False
    )
    # NODO change datetimes to UTC format
    updated: db.Mapped[datetime] = db.mapped_column(
        db.DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        nullable=False
    )
    active: db.Mapped[bool] = db.mapped_column(
        default=True,
        index=True
    )

    def to_json(self):
        object_dict = dict()
        for column in inspect(self).mapper.column_attrs:
            value = getattr(self, column.key)
            if isinstance(value, datetime):
                object_dict[column.key] = value.isoformat()
            elif isinstance(value, BaseModel):
                object_dict[column.key] = value.to_json()
            else:
                object_dict[column.key] = value

        return object_dict

    # NODO 1000: implement __eq__()

    @classmethod
    def post(cls, model_object):
        if not isinstance(model_object, cls):
            return None
        if model_object.id:
            return None
        try:
            db.session.add(model_object)
            db.session.commit()
        except BaseException as e:
            print(e)
            db.session.rollback()
            return None
        return model_object

    @classmethod
    def get(cls, id: UUID):
        model_object = db.session.scalar(select(cls).where(cls.id == id).where(cls.active == True))
        return model_object

    @classmethod
    def patch(cls, id: UUID, **kwargs):
        model_object = cls.get(id)
        if not model_object:
            return None
        for key, value in kwargs.items():
            try:
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
                db.session.rollback()
                return None

    @classmethod
    def put(cls, model_object):
        if not model_object.id:
            return None
        try:
            db.session.add(model_object)
            db.session.commit()
        except BaseException as e:
            print(e)
            db.session.rollback()
            return None
        return model_object

    @classmethod
    def delete(cls, id: UUID):
        model_object = cls.get(id)
        if not model_object:
            return False
        model_object.active = False
        try:
            db.session.add(model_object)
            db.session.commit()
            return True
        except BaseException as e:
            print(e)
            db.session.rollback()
            return False


class BaseSchema(ma.SQLAlchemyAutoSchema):

    @post_load(pass_many=True)
    def make_model(self, data, **kwargs):
        return self.Meta.model(**data)
