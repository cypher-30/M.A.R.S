"""Test fixtures.

The whole suite runs on an in-memory SQLite database, so `pytest` works with no
Docker, no Postgres, and no network. That is deliberate: if a test needs
infrastructure, it won't get run, and a test that doesn't get run isn't a test.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db import models  # noqa: F401  — registers the tables


@pytest.fixture
def session():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    with factory() as s:
        yield s
    Base.metadata.drop_all(engine)
