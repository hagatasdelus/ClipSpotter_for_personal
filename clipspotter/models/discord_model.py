from sqlalchemy import BigInteger, Enum, String, select
from sqlalchemy.orm import Mapped, mapped_column

from clipspotter.utils.database import db_session, select_session

from .base_model import BaseModel
from .category import Category


class DiscordModel(BaseModel):
    __tablename__ = "discord_users"

    guild_id: Mapped[int] = mapped_column(
        "guild_id",
        BigInteger,
        nullable=False,
        index=True,
    )
    category: Mapped[Category] = mapped_column(
        "category",
        Enum(Category),
        nullable=False,
        default=Category.UNSELECTED,
    )
    name: Mapped[str] = mapped_column(
        "set_name",
        String(64),
        nullable=True,
    )
    days_ago: Mapped[int] = mapped_column(
        "days_ago",
        nullable=True,
    )

    def __init__(self, guild_id):
        self.guild_id = guild_id

    @classmethod
    async def create_new_guild(cls, guild_id: int) -> "DiscordModel":
        async with db_session() as session:
            new_guild = cls(guild_id=guild_id)
            session.add(new_guild)
            return new_guild

    @classmethod
    async def select_guild_by_guild_id(cls, guild_id) -> "DiscordModel":
        async with select_session() as session:
            result = await session.execute(select(cls).filter_by(guild_id=guild_id))
            return result.scalars().first()

    async def update_days_by_guild_id(self, days_ago: int):
        async with db_session() as session:
            self.days_ago = days_ago
            session.add(self)

    async def save_new_cat_settings(self, category: Category, name: str):
        async with db_session() as session:
            self.category = category
            self.name = name
            session.add(self)

    async def remove_cat_settings(self):
        async with db_session() as session:
            self.category = Category.UNSELECTED
            self.name = ""
            session.add(self)
