from fastapi import APIRouter, Depends, Request
from fastapi_cache.decorator import cache
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import templates
from app.core.db import get_async_session
from app.crud.messages import message_crud
from app.dependencies import get_cookie, get_current_user
from app.models import User
from app.schemas.messages import MessageRead

router = APIRouter(prefix='/chat', tags=['Chat'])


@router.get("/chat", dependencies=[Depends(get_current_user)])
async def get(request: Request, users_access_token=Depends(get_cookie),
              current_user=Depends(get_current_user)):
    """Страница чата."""
    response = templates.TemplateResponse(
        request,
        'chat.html',
        {'token': current_user.id}
    )
    response.set_cookie(key='users_access_token', value=users_access_token)
    return response


@router.get('/messages/{user_id}', response_model=list[MessageRead])
@cache(expire=120)
async def get_messages(
    user_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Возвращает сообщения между текущим юзером и выбранным юзером."""
    return await message_crud.get_messages_between_users(
        user_id_1=user_id,
        user_id_2=current_user.id,
        session=session
    ) or []
