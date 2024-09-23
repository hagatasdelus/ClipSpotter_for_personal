import enum


class Visibility(enum.Enum):
    PUBLIC = "public"
    PRIVATE = "private"

    @classmethod
    def selectable_visibilities(cls) -> list["Visibility"]:
        return list(cls)

    @property
    def is_ephemeral(self) -> bool:
        return self == Visibility.PRIVATE
