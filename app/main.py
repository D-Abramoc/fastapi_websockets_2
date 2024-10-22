from typing import Annotated

from fastapi import (
    Cookie,
    Depends,
    FastAPI,
    Query,
    WebSocket,
    WebSocketException,
    status,
    WebSocketDisconnect,
    Response,
    Form,
    Request
)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user
from app.api.endpoints import router_users, router_messages
from app.crud.messages import message_crud
from app.core.db import get_async_session

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

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, WebSocket] = {}

    async def connect(self, client_id, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id, websocket: WebSocket):
        self.active_connections.pop(client_id)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for user, connection in self.active_connections.items():
            print(type(connection))
            await connection.send_text(message)

    async def send_message_to_user(self, message: str, user_id: str):
        for user, connection in self.active_connections.items():
            if user == user_id:
                await connection.send_text(message)


manager = ConnectionManager()


@app.get('/')
async def redirect_to_auth():
    """Редирект на страницу /auth."""
    return RedirectResponse(url='/auth_or_register')


@app.get('/auth_or_register', response_class=HTMLResponse)
async def auth_or_register(request: Request):
    return templates.TemplateResponse(
        request, 'auth_or_register.html'
    )


@app.get('/register', response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse(
        request, 'register.html'
    )



@app.get('/auth', response_class=HTMLResponse)
async def auth_page(request: Request):
    return templates.TemplateResponse(
        request, 'auth.html'
    )




@app.post('/coockie')
async def create_coockie(response: Response, member=Form()):
    response.set_cookie(key='user_access_token', value=member)
    return {'result': 'ok'}


@app.get('/checkcookie', response_class=HTMLResponse)
async def check(request: Request, user_access_token: str | None = Cookie(default=None)):
    return templates.TemplateResponse(
        request,
        'checkcookie.html',
        {'coockie': user_access_token}
    )


async def get_cookie(
    users_access_token: str | None = Cookie(default=None)
):
    return users_access_token


@app.get("/chat", dependencies=[Depends(get_current_user)])
# async def get():
#     return HTMLResponse(html)
async def get(request: Request, users_access_token=Depends(get_cookie),
              current_user=Depends(get_current_user)):
    # users_access_token = request.cookies.get('users_access_token')
    print(users_access_token)
    response = templates.TemplateResponse(
        request,
        'chat.html',
        {'token': current_user.id}
    )
    response.set_cookie(key='users_access_token', value=users_access_token)
    return response
    # return {'token': users_access_token}


async def get_cookie_or_token(
    websocket: WebSocket,
    users_access_token: Annotated[str | None, Cookie()] = None,
    token: Annotated[str | None, Query()] = None,
):
    if users_access_token is None and token is None:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    return users_access_token or token


@app.websocket("/items/{item_id}/ws")
async def websocket_endpoint(
    *,
    websocket: WebSocket,
    item_id: str,
    q: int | None = None,
    users_access_token: Annotated[str, Depends(get_cookie_or_token)],
    session: Annotated[AsyncSession, Depends(get_async_session)]
):
    await manager.connect(users_access_token, websocket)
    print(manager.active_connections)
    try:
        while True:
            data = await websocket.receive_text()
            to_recipient, message = data.split(maxsplit=1)
            await message_crud.add(
                session=session,
                sender_id=int(users_access_token),
                recipient_id=int(to_recipient),
                content=message
            )
            await manager.send_personal_message(
                f"Сообщение пользователю {to_recipient}: {message}", websocket
            )
            await manager.send_message_to_user(
                f"Сообщение от пользователя {users_access_token}: {message}",
                to_recipient
            )
    except WebSocketDisconnect:
        manager.disconnect(users_access_token, websocket)
        await manager.broadcast(f"Client #{users_access_token} left the chat")
