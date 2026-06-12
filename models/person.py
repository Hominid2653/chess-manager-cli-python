"""Base class for people in system."""


class Person:
    """Shared name and ID for admins and players."""

    def __init__(self, name: str, person_id: str):
        self.name = name
        self.person_id = person_id

    def to_dict(self) -> dict:
        """Convert person data to a dictionary for JSON storage."""
        return {"name": self.name, "person_id": self.person_id}

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r}, id={self.person_id!r})"
