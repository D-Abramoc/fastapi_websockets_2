from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.messages import MessageRead
from app.models import User
from app.dependencies import get_current_user
from app.core.db import get_async_session
from app.crud.messages import message_crud

from fastapi_cache.decorator import cache


router = APIRouter(prefix='/chat', tags=['Chat'])


@router.get('/messages/{user_id}', response_model=list[MessageRead])
@cache(expire=120)
async def get_messages(
    user_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    return await message_crud.get_messages_between_users(
        user_id_1=user_id,
        user_id_2=current_user.id,
        session=session
    ) or []
