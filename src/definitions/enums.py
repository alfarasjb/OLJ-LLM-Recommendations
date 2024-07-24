from enum import Enum


class TypeOfWork(Enum):
    FULL_TIME = "Full Time"
    PART_TIME = "Part Time"
    GIG = "Gig"
    ANY = "Any"

    @classmethod
    def work(cls, type_of_work: str):
        mapping = {
            key.lower(): value
            for key, value in cls._value2member_map_.items()
        }
        return mapping[type_of_work.lower()]
