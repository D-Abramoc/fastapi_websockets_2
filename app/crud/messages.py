from app.crud.base import CRUDBase
from app.models import Message


class CRUDMessage(CRUDBase):
    pass


message_crud = CRUDBase(Message)
