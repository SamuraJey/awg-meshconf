"""Tests for package initialization."""

import awg_meshconf


def test_version_exists():
    """Test that version is defined."""
    assert hasattr(awg_meshconf, "__version__")
    assert isinstance(awg_meshconf.__version__, str)
    assert awg_meshconf.__version__


def test_main_function_exists():
    """Test that main function is available."""
    assert hasattr(awg_meshconf, "main")
    assert callable(awg_meshconf.main)
