from sqlmodel import Session, create_engine
from pydantic import BaseModel
from utils.path import PATH
from databases.postgres.domain.models import *
from contextlib import contextmanager
from dotenv import dotenv_values

# pg_dump -E UTF-8 -U cern -d cern_db -f "H:/Codes/Demo/CERN RAG/resources/database/cern_db.sql"
# docker exec -i $(docker-compose ps -q database) psql -U cern -d cern_db < ../resources/database/cern_db.sql


class PostgresConfig(BaseModel):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    host: str
    port: int
    POSTGRES_DB: str

    @property
    def url(self):
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.host}:{self.port}/{self.POSTGRES_DB}"


config_path = PATH.postgres / "database.production.env"

config = dotenv_values(config_path)

postgres = PostgresConfig(**config)


def get_engine():
    return create_engine(postgres.url, echo=True)


@contextmanager
def get_session():
    engine = get_engine()
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()
