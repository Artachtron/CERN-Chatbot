from sqlmodel import Field, SQLModel, ForeignKey


class File(SQLModel, table=True):
    id: str = Field(primary_key=True)


class DataImage(SQLModel, table=True):
    id: str = Field(primary_key=True)
    data: bytes
    file_id: str | None = Field(default=None, foreign_key="file.id")


class DataTable(SQLModel, table=True):
    id: str = Field(primary_key=True)
    text: str
    file_id: str | None = Field(default=None, foreign_key="file.id")


class DataText(SQLModel, table=True):
    id: str = Field(primary_key=True)
    text: str
    file_id: str | None = Field(default=None, foreign_key="file.id")
