"""Configuration management for AWS Network Shell."""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from threading import Lock


class Config:
    """Configuration manager."""
    
    def __init__(self, path: Optional[Path] = None):
        self.path = path or self._get_default_config_path()
        self.data = self._load()
    
    def _get_default_config_path(self) -> Path:
        """Get default config file path."""
        return Path.home() / ".config" / "aws_network_shell" / "config.json"
    
    def _load(self) -> Dict[str, Any]:
        """Load config from file."""
        if not self.path.exists():
            return self._get_defaults()
        
        try:
            return json.loads(self.path.read_text())
        except Exception:
            return self._get_defaults()
    
    def _get_defaults(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "prompt": {
                "style": "short",  # "short" or "long"
                "theme": "catppuccin",  # "catppuccin", "dracula", or custom
                "show_indices": True,  # Show numbers like gl:1 vs gl:name
                "max_length": 50,  # Max length for long names
            },
            "display": {
                "output_format": "table",  # "table", "json", "yaml"
                "colors": True,
                "pager": False,
                "allow_truncate": False,  # If False, shows full values or advises required width
            },
            "cache": {
                "enabled": True,
                "expire_minutes": 30,
            }
        }
    
    def save(self):
        """Save configuration to file."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data, indent=2))
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation (e.g., "prompt.style")."""
        keys = key.split(".")
        value = self.data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value using dot notation."""
        keys = key.split(".")
        target = self.data
        
        # Navigate to the parent dict
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]
        
        # Set the final value
        target[keys[-1]] = value
    
    def get_prompt_style(self) -> str:
        """Get prompt style (short or long)."""
        return self.get("prompt.style", "short")
    
    def get_theme_name(self) -> str:
        """Get theme name."""
        return self.get("prompt.theme", "catppuccin")
    
    def show_indices(self) -> bool:
        """Whether to show indices in prompt."""
        return self.get("prompt.show_indices", True)
    
    def get_max_length(self) -> int:
        """Get max length for long names."""
        return self.get("prompt.max_length", 50)


def get_config() -> Config:
    """Get global config instance."""
    return Config()


class RuntimeConfig:
    """Thread-safe singleton for runtime configuration.
    
    Used by modules to access shell runtime settings (profile, regions, no_cache)
    without explicit parameter passing.
    
    Usage:
        # In shell:
        RuntimeConfig.set_profile("production")
        RuntimeConfig.set_regions(["us-east-1", "eu-west-1"])
        
        # In modules:
        client = MyClient(RuntimeConfig.get_profile())
        regions = RuntimeConfig.get_regions()
    """
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._profile: Optional[str] = None
        self._regions: list[str] = []
        self._no_cache: bool = False
        self._output_format: str = "table"
        self._initialized = True
    
    @classmethod
    def set_profile(cls, profile: Optional[str]) -> None:
        """Set AWS profile for all modules."""
        instance = cls()
        instance._profile = profile
    
    @classmethod
    def get_profile(cls) -> Optional[str]:
        """Get current AWS profile."""
        instance = cls()
        return instance._profile
    
    @classmethod
    def set_regions(cls, regions: list[str]) -> None:
        """Set target regions for discovery operations."""
        instance = cls()
        instance._regions = regions if regions else []
    
    @classmethod
    def get_regions(cls) -> list[str]:
        """Get target regions. Empty list means all regions."""
        instance = cls()
        return instance._regions
    
    @classmethod
    def set_no_cache(cls, no_cache: bool) -> None:
        """Set cache disable flag."""
        instance = cls()
        instance._no_cache = no_cache
    
    @classmethod
    def is_cache_disabled(cls) -> bool:
        """Check if caching is disabled."""
        instance = cls()
        return instance._no_cache
    
    @classmethod
    def set_output_format(cls, format: str) -> None:
        """Set output format (table, json, yaml)."""
        instance = cls()
        if format not in ("table", "json", "yaml"):
            raise ValueError(f"Invalid format: {format}")
        instance._output_format = format
    
    @classmethod
    def get_output_format(cls) -> str:
        """Get current output format."""
        instance = cls()
        return instance._output_format
    
    @classmethod
    def reset(cls) -> None:
        """Reset to defaults (mainly for testing)."""
        instance = cls()
        instance._profile = None
        instance._regions = []
        instance._no_cache = False
        instance._output_format = "table"


def get_runtime_config() -> RuntimeConfig:
    """Get global runtime config instance."""
    return RuntimeConfig()