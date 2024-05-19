from pydantic import BaseModel


class Schema(BaseModel):
    __vectorized__: list[str] = ["text"]


class Element(Schema):
    type: str
    element_id: str
    text: str
