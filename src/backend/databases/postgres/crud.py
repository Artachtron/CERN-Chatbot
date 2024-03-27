from sqlmodel import SQLModel, Session, select
from backend.databases.postgres.database import get_engine, get_session
from backend.databases.postgres.domain.models import (
    File,
    DataTable,
    DataImage,
    DataText,
)
from typing import Iterable


def with_session(func):
    def wrapper(*args, **kwargs):
        if "session" in kwargs:
            return func(*args, **kwargs)

        with get_session() as session:
            kwargs["session"] = session
            return func(*args, **kwargs)

    return wrapper


def create_tables():
    engine = get_engine()
    SQLModel.metadata.create_all(engine)


def drop_tables():
    engine = get_engine()
    SQLModel.metadata.drop_all(engine)


@with_session
def get_file_by_name(file_name: str, session: Session):
    statement = select(File).where(File.id == file_name)
    return session.exec(statement).first()


@with_session
def insert_file_content(
    file_name: str,
    content: dict[str, Iterable],
    session: Session,
):

    if (file := get_file_by_name(file_name, session=session)) is None:
        file = File(id=file_name)
        session.add(file)
        session.commit()

    images = content["images"]
    tables = content["tables"]
    texts = content["texts"]

    for image in images:
        insert_image(image, file.id, session=session)

    for table in tables:
        insert_table(table, file.id, session=session)

    for text in texts:
        insert_text(text, file.id, session=session)


@with_session
def get_table(table_id, file_id: str, session: Session):
    statement = select(DataTable).where(
        (DataTable.id == table_id) & (DataTable.file_id == file_id)
    )
    return session.exec(statement).first()


@with_session
def insert_table(table_data, file_id: str, session: Session):
    if get_table(table_data.id, file_id, session=session) is None:
        table = DataTable(id=table_data.id, text=table_data.text, file_id=file_id)
        session.add(table)
        session.commit()


@with_session
def get_text(text_id, file_id: str, session: Session):
    statement = select(DataText).where(
        (DataText.id == text_id) & (DataText.file_id == file_id)
    )
    return session.exec(statement).first()


@with_session
def insert_text(text_data, file_id: str, session: Session):
    if get_text(text_data.id, file_id, session=session) is None:
        text = DataText(id=text_data.id, text=text_data.text, file_id=file_id)
        session.add(text)
        session.commit()


@with_session
def get_image(image_name, file_id: str, session: Session):
    statement = select(DataImage).where(
        (DataImage.id == image_name) & (DataImage.file_id == file_id)
    )
    return session.exec(statement).first()


@with_session
def insert_image(image_data, file_id: str, session: Session):
    if get_image(image_data.name, file_id, session=session) is None:
        image = DataImage(
            id=image_data.name, data=image_data.image_bytes, file_id=file_id
        )
        session.add(image)
        session.commit()


def get_reference(category: str, reference: str, filename: str):
    file = get_file_by_name(filename)

    match category.lower():
        case "image":
            return get_image(reference, file.id)
        case "table":
            return get_table(reference, file.id)
        case "text":
            return get_text(reference, file.id)
