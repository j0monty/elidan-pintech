import os
from pathlib import Path
from typing import Any, Dict

from common.logger import get_logger
from dynaconf import Dynaconf

logger = get_logger(__name__)


class ConfigurationError(Exception):
    """Custom exception for configuration errors."""

    pass


def get_component_settings(component_name: str) -> Dict[str, Any]:
    """
    Get settings for a specific component.

    Args:
        component_name (str): The name of the component (e.g., 'PINTECH_API').

    Returns:
        Dict[str, Any]: A dictionary of settings for the specified component.
    """
    env = os.getenv('PINTECH_ENV', 'development')
    logger.info(f'Loading settings for component: {component_name} in environment: {env}')

    config_dir = Path('src/python/config')
    settings_files = [
        config_dir / 'settings.toml',
        config_dir / '.secrets.toml',
        config_dir / 'environments' / f'{env}.toml',
    ]

    # Check if all required files exist
    for file in settings_files:
        if not file.is_file():
            raise ConfigurationError(f'Required configuration file not found: {file}')

    settings = Dynaconf(
        envvar_prefix='PINTECH',
        settings_files=[str(f) for f in settings_files],
        environments=True,
        env=env,
    )

    logger.debug(f'Dynaconf configuration: {settings.as_dict()}')

    # Filter settings for the specific component, if none found return empty dict
    component_settings = settings.get(component_name, {})
    if not component_settings:
        raise ConfigurationError(f'No configuration found for component: {component_name}')

    logger.debug(f'Loaded settings for {component_name}: {component_settings}')

    return component_settings
