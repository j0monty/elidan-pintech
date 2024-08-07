import os
from typing import Any, Dict

from common.logger import get_logger
from dynaconf import Dynaconf

logger = get_logger(__name__)


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

    settings = Dynaconf(
        envvar_prefix='PINTECH',
        settings_files=[
            'src/python/config/settings.toml',
            'src/python/config/.secrets.toml',
            f'src/python/config/environments/{env}.toml',
        ],
        environments=True,
        env=env,
    )

    # Filter settings for the specific component
    component_settings = settings.get(component_name, {})
    logger.debug(f'Loaded settings for {component_name}: {component_settings}')

    return component_settings
