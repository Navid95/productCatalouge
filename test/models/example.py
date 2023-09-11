from app.models import BaseModel
from app.extensions import db


class Example(BaseModel):
    text: db.Mapped[str] = db.mapped_column(nullable=True)
