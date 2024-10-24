"""
В этот файл импортируются модели, чтобы alembic забирал все из одного файла.
"""

from app.core.db import Base  # noqa
from app.models import Message, User  # noqa
