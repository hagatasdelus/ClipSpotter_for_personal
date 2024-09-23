from typing import Any, Type, TypeVar

from rapidfuzz import fuzz
from sqlalchemy import select
from sqlalchemy.orm import Mapped, mapped_column

from clipspotter.config import THRESHOLD_FOR_SIMILARITY
from clipspotter.models.base_model import BaseModel
from clipspotter.utils.database import db_session, select_session

T = TypeVar("T", bound="TwitchBaseModel")


class TwitchBaseModel(BaseModel):
    __abstract__ = True

    @classmethod
    async def select_by_name(cls: Type[T], name: str, name_field: str) -> T | None:
        async with select_session() as session:
            result = await session.execute(select(cls).filter_by(**{name_field: name}))
            return result.scalars().first()

    @classmethod
    async def create(cls: Type[T], **kwargs: Any) -> T:
        async with db_session() as session:
            new_instance = cls(**kwargs)
            session.add(new_instance)
            return new_instance


class TwitchGameModel(TwitchBaseModel):
    __tablename__ = "twitch_games"

    game_name: Mapped[str] = mapped_column(
        "game_name",
        nullable=False,
        unique=True,
    )
    game_id: Mapped[str] = mapped_column(
        "game_id",
        nullable=False,
        unique=True,
    )

    @classmethod
    async def select_by_name(cls, name: str, name_field: str = "game_name") -> "TwitchGameModel | None":
        return await super().select_by_name(name, name_field)

    @classmethod
    async def select_by_normalized_name(cls, input_name: str) -> "TwitchGameModel | None":
        async with select_session() as session:
            all_records = await session.execute(select(cls))
            all_records = all_records.scalars().all()

        normalized_input = cls.normalize_name(input_name)
        best_match: "TwitchGameModel | None" = None
        highest_ratio: float = 0.0

        for record in all_records:
            record_name = record.game_name
            normalized_record_name = cls.normalize_name(record_name)
            ratio = fuzz.ratio(normalized_input, normalized_record_name)

            if ratio > highest_ratio:
                highest_ratio = ratio
                best_match = record

        if highest_ratio > THRESHOLD_FOR_SIMILARITY:
            return best_match
        return None

    @staticmethod
    def normalize_name(name: str) -> str:
        return name.strip().lower()


class TwitchStreamerModel(TwitchBaseModel):
    __tablename__ = "twitch_streamers"

    streamer_name: Mapped[str] = mapped_column(
        "streamer_name",
        nullable=False,
        unique=True,
    )
    streamer_id: Mapped[str] = mapped_column(
        "streamer_id",
        nullable=False,
        unique=True,
    )
    streamer_display_name: Mapped[str] = mapped_column(
        "display_name",
        nullable=False,
        unique=True,
    )

    @classmethod
    async def select_by_name(cls, name: str, name_field: str = "streamer_name") -> "TwitchStreamerModel | None":
        return await super().select_by_name(name, name_field)

    @classmethod
    async def select_by_display_name(cls, display_name: str) -> "TwitchStreamerModel | None":
        return await super().select_by_name(display_name, "streamer_display_name")
