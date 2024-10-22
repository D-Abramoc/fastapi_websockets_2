from typing import Annotated

from fastapi import APIRouter, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.schemas.users import UserRegister
from app.crud.users import user_crud
from app.exceptions import (
    UserAlreadyExistsException, PasswordMismatchException
)
from app.api.utils.users import get_password_hash


router = APIRouter(prefix='/auth', tags=['Auth'])

templates = Jinja2Templates(directory='templates')


@router.post('/register', response_class=HTMLResponse)
async def register(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user_data: Annotated[UserRegister, Depends(UserRegister.as_form)],
):
    """Регистрация пользователя."""
    user = await user_crud.find_one_or_none(session, email=user_data.email)
    if user:
        raise UserAlreadyExistsException
    if user_data.password != user_data.repeat_password:
        raise PasswordMismatchException('Пароли не совпадают')
    hashed_password = get_password_hash(user_data.password)
    await user_crud.add(
        session,
        email=user_data.email,
        password=hashed_password,
    )
    return templates.TemplateResponse(
        request, 'auth.html'
    )
