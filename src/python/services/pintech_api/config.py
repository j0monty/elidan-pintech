from typing import Any, Dict

from common.logger import get_logger
from config.configuration import get_component_settings
from pydantic import BaseModel, Field

logger = get_logger(__name__)


class PintechAPISettings(BaseModel):
    """Configuration settings for the Pintech API."""

    debug: bool = Field(False, description='Debug mode flag')
    api_docs_title: str = Field('PinTech API', description='Title for API documentation')
    api_docs_desc: str = Field('PinTech API Documentation', description='Description for API documentation')
    api_ver: str = Field('0.1', description='API version')
    mongo_uri: str = Field('mongodb://localhost:27017', description='MongoDB connection URI')
    mongo_timeout: int = Field(5, description='MongoDB connection timeout in seconds')

    @classmethod
    def load(cls) -> 'PintechAPISettings':
        """
        Load the settings for the Pintech API.

        Returns:
            PintechAPISettings: An instance of PintechAPISettings with loaded configuration.
        """
        settings: Dict[str, Any] = get_component_settings('PINTECH_API')
        return cls(**settings)
