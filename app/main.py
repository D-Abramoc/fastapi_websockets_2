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
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

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
            await connection.send_text(message)


manager = ConnectionManager()


@app.get('/auth', response_class=HTMLResponse)
async def auth_cookie(request: Request):
    return templates.TemplateResponse(
        request,
        'auth.html'
    )


@app.post('/coockie')
async def create_coockie(response: Response, member=Form()):
    response.set_cookie(key='fakecoockie', value=member, domain='.localhost')
    return {'result': 'ok'}


@app.get('/checkcookie', response_class=HTMLResponse)
async def check(request: Request, fakecoockie=Cookie()):
    return templates.TemplateResponse(
        request,
        'checkcookie.html',
        {'coockie': fakecoockie}
    )


async def get_cookie(
    fakecoockie=Cookie()
):
    return fakecoockie


@app.get("/chat", response_class=HTMLResponse)
async def get(request: Request, cookie=Depends(get_cookie)):
    return templates.TemplateResponse(
        request,
        'chat.html',
        {'token': cookie}
    )


async def get_cookie_or_token(
    websocket: WebSocket,
    fakecoockie: Annotated[str | None, Cookie()] = None,
    token: Annotated[str | None, Query()] = None,
):
    if fakecoockie is None and token is None:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    return fakecoockie or token


@app.websocket("/items/{item_id}/ws")
async def websocket_endpoint(
    *,
    websocket: WebSocket,
    item_id: str,
    q: int | None = None,
    cookie_or_token: Annotated[str, Depends(get_cookie_or_token)],
    # request: Request,
    # cookie=Depends(get_cookie)
):
    await manager.connect(cookie_or_token, websocket)
    print(manager.active_connections)
    print(websocket._cookies)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(
                f"Session cookie or query token value is: {cookie_or_token}", websocket
            )
            if q is not None:
                await websocket.send_text(f"Query parameter q is: {q}")
            await manager.broadcast(f"Message text was: {data}, for item ID: {item_id}")
    except WebSocketDisconnect:
        manager.disconnect(item_id, websocket)
        await manager.broadcast(f"Client #{item_id} left the chat")