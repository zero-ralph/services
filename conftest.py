import os
import pytest


os.environ["CONFIG_FILE"] = "config.test.toml"

def pytest_configure(config):
    from core.config import get_settings
    settings = get_settings()

    database_name = settings.database.database
    if not database_name.endswith("_test"):
        pytest.exit(
            f"Refusing to run tests against database '{database_name}'. "
            "The test database name must end in '_test'.",
            returncode=1,
        )