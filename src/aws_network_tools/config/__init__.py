"""Configuration management for AWS Network Shell."""

import json
from pathlib import Path
from typing import Dict, Any, Optional


class Config:
    """Configuration manager."""
    
    def __init__(self, path: Optional[Path] = None):
        self.path = path or self._get_default_config_path()
        self.data = self._load()
    
    def _get_default_config_path(self) -> Path:
        """Get default config file path."""
        return Path.home() / ".aws_network_shell" / "config.json"
    
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