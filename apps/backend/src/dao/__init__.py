"""
DAO Layer

Data Access Objects for database operations.
Each DAO inherits from BaseDAO and provides database operations for a specific model.
"""

from dao.user import user_dao

__all__: list[str] = ["user_dao"]
