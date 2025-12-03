from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import logging
import boto3
from botocore.config import Config

# Library-wide logger
logger = logging.getLogger("aws_network_tools")

# Centralized botocore configuration (timeouts, retries, UA)
DEFAULT_BOTO_CONFIG = Config(
    retries={"max_attempts": 10, "mode": "standard"},
    connect_timeout=5,
    read_timeout=20,
    user_agent_extra="aws-network-tools/0.1.0",
)


@dataclass
class Context:
    """Shell execution context"""

    type: str
    ref: str
    name: str
    data: dict = field(default_factory=dict)


class BaseClient:
    """Base client for AWS services"""

    def __init__(
        self,
        profile: Optional[str] = None,
        session: Optional[boto3.Session] = None,
        max_workers: Optional[int] = None,
    ):
        if session:
            self.session = session
            self.profile = (
                profile  # Keep profile for reference, but use provided session
            )
        else:
            self.session = (
                boto3.Session(profile_name=profile) if profile else boto3.Session()
            )
            self.profile = profile
        # Concurrency control for modules using thread pools
        import os

        self.max_workers = max_workers or int(os.getenv("AWS_NET_MAX_WORKERS", "10"))

    def client(self, service: str, region_name: Optional[str] = None):
        """Create a boto3 client with standardized config."""
        try:
            return self.session.client(
                service, region_name=region_name, config=DEFAULT_BOTO_CONFIG
            )
        except Exception as e:
            logger.warning(
                "Failed to create client for %s (region=%s): %s",
                service,
                region_name,
                e,
            )
            # Fallback without custom config
            return self.session.client(service, region_name=region_name)


class ModuleInterface(ABC):
    """Interface for AWS service modules"""

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the module (e.g., 'vpc')"""
        pass

    @property
    def commands(self) -> Dict[str, str]:
        """Dictionary of {command_name: help_text} available at root level"""
        return {}

    @property
    def context_commands(self) -> Dict[str, List[str]]:
        """Dictionary of {context_name: [command_names]}"""
        return {}

    @property
    def show_commands(self) -> Dict[str, List[str]]:
        """Dictionary of {context_name: [show_options]}"""
        return {}

    @abstractmethod
    def execute(self, shell: Any, command: str, args: str):
        """Execute a command provided by this module"""
        pass
