import os

from common.logger import get_logger
from dynaconf import Dynaconf
from pydantic import BaseModel

current_dir = os.path.dirname(os.path.abspath(__file__))
logger = get_logger(__name__)


class Settings(BaseModel):
    """Base settings class using dynaconf and Pydantic."""

    @classmethod
    def from_dynaconf(cls, prefix: str) -> 'Settings':
        """
        Create a Settings instance from dynaconf configuration.

        Args:
            prefix (str): The prefix to filter settings.

        Returns:
            Settings: An instance of the Settings class with filtered configuration.
        """
        logger.info(f'Loading settings with prefix: {prefix}')
        dynaconf_settings = Dynaconf(
            envvar_prefix='DYNACONF',
            settings_files=[os.path.join(current_dir, 'settings.toml'), os.path.join(current_dir, '.secrets.toml')],
            environments=True,
        )

        logger.debug(f'All settings: {dynaconf_settings.as_dict()}')

        # Filter settings based on the prefix
        filtered_settings = {
            k[len(prefix) + 1 :]: v for k, v in dynaconf_settings.as_dict().items() if k.startswith(f'{prefix}_')
        }
        logger.debug(f'Filtered settings for {prefix}: {filtered_settings}')
        return cls(**filtered_settings)

    class Config:
        extra = 'allow'  # Allow extra fields for flexibility


# Create a function to get settings for a specific component
def get_component_settings(component_name: str) -> Settings:
    """
    Get settings for a specific component.

    Args:
        component_name (str): The name of the component.

    Returns:
        Settings: An instance of the Settings class for the specified component.
    """
    logger.info(f'Getting settings for component: {component_name}')
    settings = Settings.from_dynaconf(component_name.upper())
    logger.debug(f'Retrieved settings for {component_name}: {settings.dict()}')
    return settings


# `envvar_prefix` = export envvars with `export DYNACONF_FOO=bar`.
# `settings_files` = Load these files in the order.
