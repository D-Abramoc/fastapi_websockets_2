from fastapi import WebSocket

from app.core.db import AsyncSessionLocal
from app.crud.users import user_crud
from app.models import User
from app.worker import send_notification


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
        for _, connection in self.active_connections.items():
            await connection.send_text(message)

    async def send_message_to_user(self, message: str, user_id: str,):
        if user_id not in self.active_connections:
            async with AsyncSessionLocal() as session:
                user: User = await user_crud.find_one_or_none(
                    session, id=int(user_id)
                )
            if user is None:
                pass
            else:
                send_notification.delay(user.tg_id, 'You have a message')
        connection = self.active_connections[user_id]
        await connection.send_text(message)


manager = ConnectionManager()
