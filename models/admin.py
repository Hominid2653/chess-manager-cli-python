"""Admin model with credential verification for tournament management."""

import hashlib

from models.person import Person


class Admin(Person):
    """Tournament administrator with login credentials and full management access."""

    def __init__(self, name: str, admin_id: str, username: str, password_hash: str):
        super().__init__(name, admin_id)
        self.username = username
        # Stored as SHA-256 hex digest; never persist plain-text passwords.
        self.password_hash = password_hash

    @staticmethod
    def hash_password(password: str) -> str:
        """Return a SHA-256 hash of the given password."""
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def verify_password(self, password: str) -> bool:
        """Check whether the provided password matches the stored hash."""
        return self.password_hash == self.hash_password(password)

    def to_dict(self) -> dict:
        """Serialize admin account data for JSON storage."""
        return {
            **super().to_dict(),
            "admin_id": self.person_id,
            "username": self.username,
            "password_hash": self.password_hash,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Admin":
        """Rebuild an Admin instance from persisted JSON data."""
        return cls(
            name=data["name"],
            admin_id=data.get("admin_id", data.get("person_id", "")),
            username=data["username"],
            password_hash=data["password_hash"],
        )
