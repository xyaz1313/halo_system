"""Shared test fixtures: engine, session, client, sample data, event bus reset."""

import pytest
from sqlalchemy import event
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from fastapi.testclient import TestClient

from backend.db.engine import get_db
from backend.events.bus import bus
from backend.main import app

# Import all models so SQLModel.metadata knows every table
import backend.models  # noqa: F401


# ---------------------------------------------------------------------------
# Engine & session fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(name="engine", scope="module")
def fixture_engine():
    """In-memory SQLite engine shared across a test module."""
    eng = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(eng, "connect")
    def _set_pragma(dbapi_conn, _connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return eng


@pytest.fixture(name="session")
def fixture_session(engine):
    """Fresh tables + session per test; drops tables after."""
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="client")
def fixture_client(session):
    """TestClient wired to the test session via dependency override."""

    def _override_get_db():
        yield session

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as tc:
        yield tc
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Event bus reset
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _reset_event_bus():
    """Clear event bus subscriptions before each test."""
    bus.reset()
    yield
    bus.reset()


# ---------------------------------------------------------------------------
# Sample data fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(name="sample_account")
def fixture_sample_account(session):
    """A pre-created account."""
    from backend.accounts.service import create_account

    return create_account(
        session,
        email="alice@example.com",
        patient_name="Alice",
        patient_age=72,
        patient_diagnosis_stage="mild",
        patient_notes="test account",
    )


@pytest.fixture(name="sample_anchor_public")
def fixture_sample_anchor_public(session):
    """A public anchor (no owner)."""
    from backend.devices.service import create_anchor

    return create_anchor(session, label="Lobby Anchor", visibility="public")


@pytest.fixture(name="sample_anchor_private")
def fixture_sample_anchor_private(session, sample_account):
    """A private anchor owned by sample_account."""
    from backend.devices.service import create_anchor

    return create_anchor(
        session,
        label="Private Anchor",
        visibility="private",
        owner_account_id=sample_account.id,
    )


@pytest.fixture(name="sample_tag")
def fixture_sample_tag(session, sample_account):
    """A tag belonging to sample_account."""
    from backend.devices.service import create_tag

    return create_tag(session, sample_account.id, label="Alice Tag")
