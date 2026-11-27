"""Rend les tests des paquets `src` découvrables depuis la racine."""

from allelefounder.accounts.tests.test_models import UserManagerTests
from allelefounder.common.tests.test_logging import SafeJsonFormatterTests
from allelefounder.config.tests.test_environment import EnvironmentTests
from allelefounder.config.tests.test_health import HealthTests

__all__ = [
    "EnvironmentTests",
    "HealthTests",
    "SafeJsonFormatterTests",
    "UserManagerTests",
]
