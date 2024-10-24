from typing import Annotated

from fastapi import Depends, FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.endpoints import router_messages, router_users
from app.api.utils.messages import manager
from app.core.db import get_async_session
from app.crud.messages import message_crud
from app.dependencies import get_cookie_or_token
from app.exceptions import (NoJwtException, TokenExpiredException,
                            TokenNoFoundException)
from app.redis_app import redis as r

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(router_users)
app.include_router(router_messages)


@app.on_event("startup")
async def startup_event():
    FastAPICache.init(RedisBackend(redis=r), prefix='fastapi-cache')


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get('/')
async def redirect_to_auth():
    """Редирект на страницу авторизации и регистрации."""
    return RedirectResponse(url='/auth/auth_or_register')


@app.exception_handler(TokenExpiredException)
async def token_expired_exception_handler(
    request: Request, exc: HTTPException
):
    """Редирект на страницу авторизации, если истек токен."""
    return RedirectResponse(url='/auth/auth')


@app.exception_handler(TokenNoFoundException)
async def token_no_found_exception_handler(
    request: Request, exc: HTTPException
):
    """Редирект на страницу авторизации, если токен не найден."""
    return RedirectResponse(url='/auth/auth')


@app.exception_handler(NoJwtException)
async def not_validated_token(
    request: Request, exc: HTTPException
):
    """Редирект на страницу авторизации, если токен не валидный."""
    return RedirectResponse(url='/auth/auth')


@app.websocket("/items/{item_id}/ws")
async def websocket_endpoint(
    *,
    websocket: WebSocket,
    item_id: str,
    q: int | None = None,
    nik_ws: Annotated[str, Depends(get_cookie_or_token)],
    session: Annotated[AsyncSession, Depends(get_async_session)]
):
    await manager.connect(nik_ws, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                to_recipient, message = data.split(maxsplit=1)
            except ValueError:
                to_recipient = data.strip()
                message = 'Ничего не сказал'
            try:
                await message_crud.add(
                    session=session,
                    sender_id=int(nik_ws),
                    recipient_id=int(to_recipient),
                    content=message
                )
                await manager.send_personal_message(
                    f"Сообщение пользователю {to_recipient}: {message}",
                    websocket
                )
                await manager.send_message_to_user(
                    f"Сообщение от пользователя {nik_ws}: {message}",
                    to_recipient
                )
            except Exception:
                pass
    except WebSocketDisconnect:
        manager.disconnect(nik_ws, websocket)
        await manager.broadcast(f"Client #{nik_ws} left the chat")
