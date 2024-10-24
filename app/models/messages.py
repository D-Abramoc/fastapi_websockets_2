from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Message(Base):
    sender_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'))
    recipient_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'))
    content: Mapped[str] = mapped_column(Text)
