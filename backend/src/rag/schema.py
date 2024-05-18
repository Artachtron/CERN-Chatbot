from pydantic import BaseModel


class Schema(BaseModel):
    __vectorized__: list[str] = []
