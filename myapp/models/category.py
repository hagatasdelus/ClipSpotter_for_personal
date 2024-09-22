import enum


class Category(enum.Enum):
    STREAMER = "streamers"
    GAME = "games"
    UNSELECTED = "unselected"

    @classmethod
    def selectable_categories(cls) -> list["Category"]:
        return [c for c in cls if c != cls.UNSELECTED]

    @property
    def display_name(self) -> str:
        return self.value.capitalize()
