import inspect
from typing import Type

from fastapi import Form
from pydantic import BaseModel, EmailStr, Field


def as_form(cls: Type[BaseModel]):
    new_parameters = []

    for field_name, model_field in cls.model_fields.items():

        new_parameters.append(
             inspect.Parameter(
                 model_field.alias,
                 inspect.Parameter.POSITIONAL_ONLY,
                 default=Form(...) if model_field.is_required else Form(model_field.default),
                 annotation=model_field.annotation,
             )
         )

    async def as_form_func(**data):
        return cls(**data)

    sig = inspect.signature(as_form_func)
    sig = sig.replace(parameters=new_parameters)
    as_form_func.__signature__ = sig  # type: ignore
    setattr(cls, 'as_form', as_form_func)
    return cls


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
        return cls(email=email, password=password, repeat_password=repeat_password)


class SUserAuth(BaseModel):
    email: EmailStr = Field(..., description='Электронная почта')
    password: str = Field(
        ..., min_length=5, max_length=50,
        description='Пароль, от 5 до 50 знаков'
    )


class SUserRead(BaseModel):
    id: int = Field(..., description='Идентификатор пользователя')
    name: str = Field(
        ..., min_length=3, max_length=50,
        description='Имя, от 3 до 50 символов'
    )
