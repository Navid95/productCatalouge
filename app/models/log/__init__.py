from app.extensions import db


class IncomingAPI(db.Model):
    id: db.Mapped[int] = db.mapped_column(
        primary_key=True,
        autoincrement=True
    )
    url: db.Mapped[str] = db.mapped_column(db.String, nullable=False)
    method: db.Mapped[str] = db.mapped_column(db.String, nullable=False)
    headers: db.Mapped[str] = db.mapped_column(db.String)
    body: db.Mapped[str] = db.mapped_column(db.String)

    status_code: db.Mapped[str] = db.mapped_column(db.String)
    status: db.Mapped[str] = db.mapped_column(db.String)
    r_headers: db.Mapped[str] = db.mapped_column(db.String)
    r_body: db.Mapped[str] = db.mapped_column(db.String)

    remote_address: db.Mapped[str] = db.mapped_column(db.String)
