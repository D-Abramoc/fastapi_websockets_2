from typing import Annotated

from fastapi import APIRouter, Request, Form, Depends, Response
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.schemas.users import UserRegister, UserAuth
from app.crud.users import user_crud
from app.exceptions import (
    UserAlreadyExistsException, PasswordMismatchException,
    IncorrectEmailOrPasswordException
)
from app.api.utils.users import (
    get_password_hash, authenticate_user, create_access_token
)
from app.api.utils.users import create_coockie  


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
        request, 'register_success.html'
    )


@router.post('/auth',)
async def auth_cookie(
    request: Request,
    response: Response,
    user_data: Annotated[UserAuth, Depends(UserAuth.as_form)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    """Аутентификация пользователя и установка куки."""
    check = await authenticate_user(
        email=user_data.email,
        password=user_data.password,
        session=session
    )
    if check is None:
        raise IncorrectEmailOrPasswordException
    access_token = create_access_token({'sub': str(check.id)})
    response = templates.TemplateResponse(
        request,
        'auth_success.html',
        {'token': access_token}
    )
    # create_coockie(response=response, member=access_token)
    response.set_cookie(
        key='users_access_token', value=access_token, httponly=True,
    )
    return response
    # return {'token': access_token}
