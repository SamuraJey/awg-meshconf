"""Shared test fixtures and configuration."""

import pathlib
import shutil
import tempfile

import pytest

from awg_meshconf.database_manager import DatabaseManager


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_path = pathlib.Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def db_manager(temp_dir):
    """Create a DatabaseManager instance with temporary database."""
    db_path = temp_dir / "test.db"
    return DatabaseManager(db_path)


@pytest.fixture
def initialized_db(db_manager):
    """Create and initialize a database."""
    db_manager.init()
    return db_manager


@pytest.fixture
def sample_peer_data():
    """Sample peer data for testing."""
    return {
        "Name": "test_peer",
        "Address": ["10.0.0.1/24"],
        "Endpoint": "example.com:51820",
        "ListenPort": 51820,
        "PrivateKey": "test_private_key",
        "PublicKey": "test_public_key",
    }
