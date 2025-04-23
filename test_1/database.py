from contextlib import contextmanager
from collections.abc import Generator

from sqlmodel import Session, create_engine


sqlite_file_name = "database.db"
sqlite_url = f"sqlite+pysqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, echo=True)


def db_session() -> Generator[Session, None, None]:
    with Session(engine) as s:
        yield s


@contextmanager
def create_session() -> Generator[Session, None, None]:
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()
