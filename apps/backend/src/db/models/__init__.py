"""
Database Models

SQLModel definitions for database tables.
Each model should be in its own file under this directory.
"""

from db.models.user import User

__all__: list[str] = ["User"]
