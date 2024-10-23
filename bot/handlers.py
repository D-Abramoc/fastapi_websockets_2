from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message


router = Router()


@router.message(Command('start'))
async def start(message: Message):
    await message.answer(message.text)


@router.message()
async def echo(message: Message):
    await message.answer(message.text)
