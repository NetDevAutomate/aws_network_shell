"""Theme system for AWS Network Shell."""

from pathlib import Path
from typing import Dict, Any, Optional
import json


class Theme:
    """Color theme for prompts and UI."""
    
    def __init__(self, name: str, colors: Dict[str, str]):
        self.name = name
        self.colors = colors
    
    def get(self, key: str, default: str = "white") -> str:
        """Get color for a context type."""
        return self.colors.get(key, default)


# Built-in themes
DRACULA_THEME = Theme("dracula", {
    "root": "#f8f8f2",           # Foreground
    "global-network": "#bd93f9", # Purple
    "core-network": "#ff79c6",   # Pink
    "route-table": "#8be9fd",    # Cyan
    "vpc": "#50fa7b",            # Green
    "transit-gateway": "#ffb86c", # Orange
    "firewall": "#ff5555",       # Red
    "elb": "#f1fa8c",           # Yellow
    "vpn": "#6272a4",            # Comment
    "ec2-instance": "#bd93f9",   # Purple
    "prompt_separator": "#6272a4",
    "prompt_text": "#f8f8f2",
})

# Catppuccin variants
CATPPUCCIN_LATTE_THEME = Theme("catppuccin-latte", {
    "root": "#4c4f69",
    "global-network": "#8839ef",
    "core-network": "#ea76cb",
    "route-table": "#04a5e5",
    "vpc": "#40a02b",
    "transit-gateway": "#fe640b",
    "firewall": "#d20f39",
    "elb": "#df8e1d",
    "vpn": "#6c6f85",
    "ec2-instance": "#8839ef",
    "prompt_separator": "#6c6f85",
    "prompt_text": "#4c4f69",
})

CATPPUCCIN_MACCHIATO_THEME = Theme("catppuccin-macchiato", {
    "root": "#cad3f5",
    "global-network": "#c6a0f6",
    "core-network": "#f5bde6",
    "route-table": "#7dc4e4",
    "vpc": "#a6da95",
    "transit-gateway": "#f5a97f",
    "firewall": "#ed8796",
    "elb": "#eed49f",
    "vpn": "#939ab7",
    "ec2-instance": "#c6a0f6",
    "prompt_separator": "#939ab7",
    "prompt_text": "#cad3f5",
})

CATPPUCCIN_MOCHA_THEME = Theme("catppuccin-mocha", {
    "root": "#cdd6f4",
    "global-network": "#cba6f7",
    "core-network": "#f5c2e7",
    "route-table": "#89dceb",
    "vpc": "#a6e3a1",
    "transit-gateway": "#fab387",
    "firewall": "#f38ba8",
    "elb": "#f9e2af",
    "vpn": "#6c7086",
    "ec2-instance": "#cba6f7",
    "prompt_separator": "#6c7086",
    "prompt_text": "#cdd6f4",
})

# Default theme (Mocha - the darkest Catppuccin variant)
DEFAULT_THEME = CATPPUCCIN_MOCHA_THEME


def load_theme_from_file(path: Path) -> Optional[Theme]:
    """Load theme from JSON file."""
    if not path.exists():
        return None
    
    try:
        data = json.loads(path.read_text())
        return Theme(data.get("name", "custom"), data.get("colors", {}))
    except Exception:
        return None


def get_theme_dir() -> Path:
    """Get themes directory."""
    return Path.home() / ".aws_network_shell" / "themes"


def load_theme(name: Optional[str] = None) -> Theme:
    """Load theme by name or from config."""
    if name:
        # Check builtin themes
        if name.lower() == "dracula":
            return DRACULA_THEME
        if name.lower() in {"catppuccin", "catpuccin"}:  # Common misspelling
            return CATPPUCCIN_THEME
        
        # Check custom themes directory
        theme_dir = get_theme_dir()
        theme_file = theme_dir / f"{name}.json"
        if theme_file.exists():
            custom_theme = load_theme_from_file(theme_file)
            if custom_theme:
                return custom_theme
    
    # Fall back to default
    return DEFAULT_THEME