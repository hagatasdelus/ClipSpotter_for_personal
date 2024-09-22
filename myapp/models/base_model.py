from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


Base_Model = Base


class BaseModel(Base_Model):
    __abstract__ = True

    id: Mapped[int] = mapped_column("id", primary_key=True)
