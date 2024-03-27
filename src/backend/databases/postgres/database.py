from sqlmodel import Session, create_engine
from pydantic import BaseModel
import yaml
from backend.utils.path import PATH
from backend.databases.postgres.domain.models import *
from contextlib import contextmanager


class PostgresConfig(BaseModel):
    user: str
    password: str
    host: str
    port: int
    database: str

    @property
    def url(self):
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


config_path = PATH.postgres / "database.yaml"

with open(config_path) as config_file:
    Postgres = PostgresConfig(**yaml.safe_load(config_file))


def get_engine():
    return create_engine(Postgres.url, echo=True)


@contextmanager
def get_session():
    engine = get_engine()
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()
