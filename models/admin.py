"""Admin account model with login support."""

import hashlib

from models.person import Person


class Admin(Person):
    """Tournament administrator who can manage players, pairings, and results."""

    def __init__(self, name: str, admin_id: str, username: str, password_hash: str):
        super().__init__(name, admin_id)
        self.username = username
        self.password_hash = password_hash

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a plain-text password for secure storage."""
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def verify_password(self, password: str) -> bool:
        """Check if the given password matches the stored hash."""
        return self.password_hash == self.hash_password(password)

    def to_dict(self) -> dict:
        """Convert admin data to a dictionary for JSON storage."""
        return {
            **super().to_dict(),
            "admin_id": self.person_id,
            "username": self.username,
            "password_hash": self.password_hash,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Admin":
        """Create an Admin instance from saved JSON data."""
        return cls(
            name=data["name"],
            admin_id=data.get("admin_id", data.get("person_id", "")),
            username=data["username"],
            password_hash=data["password_hash"],
        )
