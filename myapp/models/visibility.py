import enum


class Visibility(enum.Enum):
    PUBLIC = "public"
    PRIVATE = "private"

    @classmethod
    def selectable_visibilities(cls):
        return [value for value in cls]

    @property
    def is_ephemeral(self):
        return self == Visibility.PRIVATE
