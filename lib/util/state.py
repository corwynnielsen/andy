from enum import StrEnum, auto


class State(StrEnum):
    DRAFT = auto()
    IN_PROGRESS = auto()
    DONE = auto()
    CANCELLED = auto()
