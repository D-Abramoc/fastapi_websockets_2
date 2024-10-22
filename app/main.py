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

from app.api.endpoints import router_users

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(router_users)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>

        <hr>

        <hr>
        <form action="" onsubmit="sendMessage(event)">
            <label>Item ID: <input type="text" id="itemId" autocomplete="off" value="foo"/></label>
            <label>Token: <input type="text" id="token" autocomplete="off" value""/></label>
            <button onclick="connect(event)">Connect</button>
            <hr>
            <label>Message: <input type="text" id="messageText" autocomplete="off"/></label>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
        var ws = null;
            function connect(event) {
                var itemId = document.getElementById("itemId")
                var token = document.getElementById("token")
                ws = new WebSocket("ws://localhost:8000/items/" + itemId.value + "/ws?token=" + token.value);
                ws.onopen = () => console.log('Websocket connected')
                ws.onmessage = function(event) {
                    var messages = document.getElementById('messages')
                    var message = document.createElement('li')
                    var content = document.createTextNode(event.data)
                    message.appendChild(content)
                    messages.appendChild(message)
                };
                ws.onclose = () => console.log('Websocket disconnected')
                event.preventDefault()
            }
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>

"""


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


@app.get("/chat",)
# async def get():
#     return HTMLResponse(html)
async def get(request: Request, users_access_token=Depends(get_cookie)):
    # users_access_token = request.cookies.get('users_access_token')
    print(users_access_token)
    response = templates.TemplateResponse(
        request,
        'chat.html',
        {'token': users_access_token}
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
    cookie=Depends(get_cookie)
):
    await manager.connect(users_access_token, websocket)
    print(manager.active_connections)
    print(cookie)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(
                f"Session cookie or query token value is: {users_access_token}", websocket
            )
            if q is not None:
                await websocket.send_text(f"Query parameter q is: {q}")
            await manager.broadcast(f"Message text was: {data}, for item ID: {item_id}")
    except WebSocketDisconnect:
        manager.disconnect(item_id, websocket)
        await manager.broadcast(f"Client #{item_id} left the chat")