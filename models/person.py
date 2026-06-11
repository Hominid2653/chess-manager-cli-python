"""Base person model shared by Admin and Player."""


class Person:
    """Represents any person in the tournament system (admin or player)."""

    def __init__(self, name: str, person_id: str):
        # Display name used across CLI output and standings tables.
        self.name = name
        # Unique identifier (e.g. P001 for players, A001 for admins).
        self.person_id = person_id

    def to_dict(self) -> dict:
        """Serialize core person fields for JSON persistence."""
        return {"name": self.name, "person_id": self.person_id}

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r}, id={self.person_id!r})"
