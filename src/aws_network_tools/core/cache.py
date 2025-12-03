"""Generic file-based cache with TTL and account safety"""

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Any

CACHE_DIR = Path.home() / ".cache" / "aws-network-tools"
CONFIG_FILE = CACHE_DIR / "config.json"
DEFAULT_TTL = 900  # 15 minutes


def parse_ttl(value: str) -> int:
    """Parse TTL string like '15m', '1h', '2d' to seconds"""
    match = re.match(r"^(\d+)([mhd]?)$", value.lower())
    if not match:
        raise ValueError(
            f"Invalid TTL format: {value}. Use number with optional m/h/d suffix"
        )
    num = int(match.group(1))
    unit = match.group(2) or "m"
    multipliers = {"m": 60, "h": 3600, "d": 86400}
    return num * multipliers[unit]


def get_default_ttl() -> int:
    """Get default TTL from config or use default"""
    if CONFIG_FILE.exists():
        try:
            config = json.loads(CONFIG_FILE.read_text())
            return config.get("ttl_seconds", DEFAULT_TTL)
        except Exception:
            pass
    return DEFAULT_TTL


def set_default_ttl(ttl_seconds: int) -> None:
    """Set default TTL in config"""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    config = {}
    if CONFIG_FILE.exists():
        try:
            config = json.loads(CONFIG_FILE.read_text())
        except Exception:
            pass
    config["ttl_seconds"] = ttl_seconds
    CONFIG_FILE.write_text(json.dumps(config))


class Cache:
    def __init__(self, namespace: str):
        self.namespace = namespace
        self.cache_file = CACHE_DIR / f"{namespace}.json"

    def _ensure_dir(self):
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)

    def get(
        self, ignore_expiry: bool = False, current_account: Optional[str] = None
    ) -> Optional[dict]:
        """Get cached data if available, not expired, and same account"""
        if not self.cache_file.exists():
            return None
        try:
            raw = json.loads(self.cache_file.read_text())

            # Check account mismatch
            if (
                current_account
                and raw.get("account_id")
                and raw["account_id"] != current_account
            ):
                self.clear()
                return None

            if not ignore_expiry:
                cached_at = datetime.fromisoformat(raw["cached_at"])  # aware
                ttl = raw.get("ttl_seconds", get_default_ttl())
                now = datetime.now(timezone.utc)
                if (now - cached_at).total_seconds() > ttl:
                    return None
            return raw.get("data")
        except Exception:
            return None

    def set(
        self,
        data: Any,
        ttl_seconds: Optional[int] = None,
        account_id: Optional[str] = None,
    ) -> None:
        """Set cache with data, TTL, and account ID"""
        self._ensure_dir()
        raw = {
            "data": data,
            "cached_at": datetime.now(timezone.utc).isoformat(),
            "ttl_seconds": ttl_seconds or get_default_ttl(),
            "account_id": account_id,
        }
        self.cache_file.write_text(json.dumps(raw, default=str))

    def clear(self) -> None:
        """Clear the cache"""
        if self.cache_file.exists():
            self.cache_file.unlink()

    def get_info(self) -> Optional[dict]:
        """Get cache metadata"""
        if not self.cache_file.exists():
            return None
        try:
            raw = json.loads(self.cache_file.read_text())
            cached_at = datetime.fromisoformat(raw["cached_at"])  # aware
            ttl = raw.get("ttl_seconds", get_default_ttl())
            now = datetime.now(timezone.utc)
            age = (now - cached_at).total_seconds()
            return {
                "cached_at": cached_at,
                "ttl_seconds": ttl,
                "age_seconds": age,
                "expired": age > ttl,
                "account_id": raw.get("account_id"),
            }
        except Exception:
            return None
