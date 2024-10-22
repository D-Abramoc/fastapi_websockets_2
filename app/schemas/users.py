import inspect
from typing import Type

from fastapi import Form
from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    email: EmailStr = Field(..., description='Электронная почта')
    password: str = Field(
        ..., min_length=5, max_length=50,
        description='Пароль, от 5 до 50 знаков'
    )
    repeat_password: str = Field(
        ..., min_length=5, max_length=50,
        description='Пароль, от 5 до 50 знаков'
    )

    @classmethod
    def as_form(
        cls,
        email: EmailStr = Form(...),
        password: str = Form(...),
        repeat_password: str = Form(...)
    ):
        return cls(
            email=email, password=password, repeat_password=repeat_password
        )


class UserAuth(BaseModel):
    email: EmailStr = Field(..., description='Электронная почта')
    password: str = Field(
        ..., min_length=5, max_length=50,
        description='Пароль, от 5 до 50 знаков'
    )

    @classmethod
    def as_form(
        cls,
        email: EmailStr = Form(...),
        password: str = Form(...),
    ):
        return cls(
            email=email, password=password,
        )


class SUserRead(BaseModel):
    id: int = Field(..., description='Идентификатор пользователя')
    name: str = Field(
        ..., min_length=3, max_length=50,
        description='Имя, от 3 до 50 символов'
    )
