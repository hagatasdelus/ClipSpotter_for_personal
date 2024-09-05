import enum


class Category(enum.Enum):
    STREAMER = "streamers"
    GAME = "games"
    UNSELECTED = "unselected"

    @classmethod
    def from_string(cls, category: str):
        category = category.lower()
        for cat in cls.selectable_categories():
            if cat.value == category:
                return cat

    @classmethod
    def selectable_categories(cls):
        return [c for c in cls if c != cls.UNSELECTED]

    def validate(self) -> bool:
        return self in (self.STREAMER, self.GAME)

    @property
    def display_name(self):
        return self.value.capitalize()
