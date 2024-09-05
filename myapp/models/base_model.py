from sqlalchemy.orm import declarative_base, Mapped, mapped_column


Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column("id", primary_key=True)
