"""Configuration loader for Yuque SDK tests."""

from pathlib import Path
from typing import Any

import yaml


class TestConfig:
    """Configuration manager for test settings."""

    _instance: "TestConfig | None" = None
    _config: dict[str, Any] = {}

    def __new__(cls) -> "TestConfig":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self) -> None:
        """Load configuration from config.yaml file."""
        config_path = Path(__file__).parent.parent / "config.yaml"

        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                self._config = yaml.safe_load(f) or {}
        else:
            self._config = {}

    @property
    def api_token(self) -> str:
        """Get the API token for testing."""
        return self._config.get("api_token", "")

    @property
    def test_group_login(self) -> str:
        """Get the test group login."""
        return self._config.get("test_group_login", "")

    @property
    def test_book_slug(self) -> str:
        """Get the test book slug."""
        return self._config.get("test_book", {}).get("slug", "")

    @property
    def test_book_id(self) -> int:
        """Get the test book ID."""
        return self._config.get("test_book", {}).get("id", 0)

    @property
    def default_offset(self) -> int:
        """Get the default pagination offset."""
        return self._config.get("pagination", {}).get("default_offset", 0)

    @property
    def default_limit(self) -> int:
        """Get the default pagination limit."""
        return self._config.get("pagination", {}).get("default_limit", 100)

    @property
    def search_keyword(self) -> str:
        """Get the default search keyword."""
        return self._config.get("search", {}).get("default_keyword", "AI")

    @property
    def search_type(self) -> str:
        """Get the default search type."""
        return self._config.get("search", {}).get("default_type", "doc")

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by key."""
        return self._config.get(key, default)


def get_config() -> TestConfig:
    """Get the test configuration singleton."""
    return TestConfig()
