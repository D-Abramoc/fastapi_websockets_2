from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import User
from app.exceptions import NoUserIdException


class CRUDUser(CRUDBase):
    pass


user_crud = CRUDUser(User)
