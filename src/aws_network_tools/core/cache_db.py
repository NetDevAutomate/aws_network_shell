"""Persistent cache storage using SQLite.

Provides save/load for routing cache and general topology cache.
Supports future web frontend with standard SQL queries.
"""

import sqlite3
import json
from pathlib import Path
from typing import Dict, Any, Optional


class CacheDB:
    """SQLite-based persistent cache storage."""

    DEFAULT_DB_PATH = Path.home() / ".config" / "aws_network_shell" / "cache.db"

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize cache database.

        Args:
            db_path: Path to SQLite database file (default: ~/.aws_network_shell/cache.db)
        """
        self.db_path = db_path or self.DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _init_schema(self):
        """Create database schema if not exists."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS routing_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,
                    resource_id TEXT,
                    resource_name TEXT,
                    region TEXT,
                    route_table_id TEXT,
                    destination TEXT,
                    target TEXT,
                    state TEXT,
                    type TEXT,
                    metadata TEXT,
                    cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    profile TEXT
                )
            """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_routing_source
                ON routing_cache(source)
            """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_routing_resource
                ON routing_cache(resource_id)
            """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_routing_destination
                ON routing_cache(destination)
            """
            )

            # General topology cache
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS topology_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cache_key TEXT NOT NULL,
                    cache_data TEXT NOT NULL,
                    cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    profile TEXT,
                    UNIQUE(cache_key, profile)
                )
            """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_topology_key
                ON topology_cache(cache_key)
            """
            )

            conn.commit()

    def save_routing_cache(
        self, cache_data: Dict[str, Any], profile: str = "default"
    ) -> int:
        """Save routing cache to database.

        Args:
            cache_data: Routing cache dict from create_routing_cache
            profile: AWS profile name

        Returns:
            Number of routes saved
        """
        with sqlite3.connect(self.db_path) as conn:
            # Clear old routes for this profile
            conn.execute("DELETE FROM routing_cache WHERE profile = ?", (profile,))

            count = 0
            for source, data in cache_data.items():
                routes = data.get("routes", [])

                for route in routes:
                    conn.execute(
                        """
                        INSERT INTO routing_cache (
                            source, resource_id, resource_name, region,
                            route_table_id, destination, target, state, type,
                            metadata, profile
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            source,
                            route.get("vpc_id")
                            or route.get("tgw_id")
                            or route.get("core_network_id"),
                            route.get("vpc_name")
                            or route.get("tgw_name")
                            or route.get("core_network_name"),
                            route.get("region"),
                            route.get("route_table"),
                            route.get("destination"),
                            route.get("target"),
                            route.get("state"),
                            route.get("type"),
                            json.dumps(
                                {
                                    k: v
                                    for k, v in route.items()
                                    if k
                                    not in [
                                        "vpc_id",
                                        "tgw_id",
                                        "core_network_id",
                                        "vpc_name",
                                        "tgw_name",
                                        "core_network_name",
                                        "region",
                                        "route_table",
                                        "destination",
                                        "target",
                                        "state",
                                        "type",
                                        "source",
                                    ]
                                }
                            ),
                            profile,
                        ),
                    )
                    count += 1

            conn.commit()
            return count

    def load_routing_cache(self, profile: str = "default") -> Dict[str, Any]:
        """Load routing cache from database.

        Args:
            profile: AWS profile name

        Returns:
            Cache dict in same format as create_routing_cache
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """
                SELECT * FROM routing_cache
                WHERE profile = ?
                ORDER BY source, resource_id, route_table_id
            """,
                (profile,),
            )

            routes_by_source = {
                "vpc": {"routes": []},
                "tgw": {"routes": []},
                "cloudwan": {"routes": []},
            }

            for row in cursor:
                route = {
                    "source": row["source"],
                    "resource_id": row["resource_id"],
                    "resource_name": row["resource_name"],
                    "region": row["region"],
                    "route_table": row["route_table_id"],
                    "destination": row["destination"],
                    "target": row["target"],
                    "state": row["state"],
                    "type": row["type"],
                }

                # Add source-specific fields
                if row["source"] == "vpc":
                    route["vpc_id"] = row["resource_id"]
                    route["vpc_name"] = row["resource_name"]
                elif row["source"] == "tgw":
                    route["tgw_id"] = row["resource_id"]
                    route["tgw_name"] = row["resource_name"]
                elif row["source"] == "cloudwan":
                    route["core_network_id"] = row["resource_id"]
                    route["core_network_name"] = row["resource_name"]
                    # Parse metadata for additional cloudwan fields
                    metadata = json.loads(row["metadata"] or "{}")
                    route.update(metadata)

                routes_by_source[row["source"]]["routes"].append(route)

            return routes_by_source

    def save_topology_cache(self, cache_key: str, data: Any, profile: str = "default"):
        """Save general topology cache entry.

        Args:
            cache_key: Cache key (e.g., 'vpcs', 'tgw', 'ec2-instances')
            data: Cache data (will be JSON serialized)
            profile: AWS profile name
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO topology_cache (cache_key, cache_data, profile, cached_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """,
                (cache_key, json.dumps(data), profile),
            )
            conn.commit()

    def load_topology_cache(
        self, cache_key: str, profile: str = "default"
    ) -> Optional[Any]:
        """Load topology cache entry.

        Args:
            cache_key: Cache key to load
            profile: AWS profile name

        Returns:
            Cached data or None if not found/expired
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT cache_data, cached_at FROM topology_cache
                WHERE cache_key = ? AND profile = ?
            """,
                (cache_key, profile),
            )

            row = cursor.fetchone()
            if not row:
                return None

            return json.loads(row[0])

    def clear_all(self, profile: Optional[str] = None):
        """Clear all cache data.

        Args:
            profile: If provided, clear only for this profile. Otherwise clear all.
        """
        with sqlite3.connect(self.db_path) as conn:
            if profile:
                conn.execute("DELETE FROM routing_cache WHERE profile = ?", (profile,))
                conn.execute("DELETE FROM topology_cache WHERE profile = ?", (profile,))
            else:
                conn.execute("DELETE FROM routing_cache")
                conn.execute("DELETE FROM topology_cache")
            conn.commit()

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT
                    COUNT(*) as total_routes,
                    COUNT(DISTINCT profile) as profiles,
                    COUNT(DISTINCT source) as sources
                FROM routing_cache
            """
            )
            routing_stats = dict(cursor.fetchone())

            cursor = conn.execute("SELECT COUNT(*) FROM topology_cache")
            topology_count = cursor.fetchone()[0]

            return {
                "routing_cache": routing_stats,
                "topology_cache": {"entries": topology_count},
                "db_size_bytes": self.db_path.stat().st_size
                if self.db_path.exists()
                else 0,
            }
