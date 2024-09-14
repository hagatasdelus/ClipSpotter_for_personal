import enum


class Visibility(enum.Enum):
    PUBLIC = "public"
    PRIVATE = "private"

    # @classmethod
    # def from_string(cls, value: str):
    #     return cls(value if value in cls._member_map_ else cls.PRIVATE)

    @classmethod
    def selectable_visibilities(cls):
        return [value for value in cls]

    @property
    def is_ephemeral(self):
        return self == Visibility.PRIVATE
