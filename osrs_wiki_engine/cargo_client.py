"""
MediaWiki Cargo API client with batching support, caching, and rate limiting.
"""
import urllib.parse
from typing import List, Dict, Any, Optional
from .cache import SQLiteCache
from .models import ItemStats, MonsterStats

class MediaWikiCargoClient:
    BASE_URL = "https://oldschool.runescape.wiki/api.php"
    USER_AGENT = "OSRS-Wiki-Engine/2.0 (contact@example.com)"

    def __init__(self, cache: Optional[SQLiteCache] = None):
        self.cache = cache or SQLiteCache(":memory:")

    def build_cargo_query_url(self, tables: str, fields: str, where: Optional[str] = None, limit: int = 50) -> str:
        params = {
            "action": "cargoquery",
            "tables": tables,
            "fields": fields,
            "limit": str(limit),
            "format": "json"
        }
        if where:
            params["where"] = where
        return f"{self.BASE_URL}?{urllib.parse.urlencode(params)}"

    def parse_item_response(self, raw_data: Dict[str, Any]) -> List[ItemStats]:
        items = []
        cargo_entries = raw_data.get("cargoquery", [])
        for entry in cargo_entries:
            title_data = entry.get("title", {})
            items.append(ItemStats.from_cargo(title_data))
        return items

    def parse_monster_response(self, raw_data: Dict[str, Any]) -> List[MonsterStats]:
        monsters = []
        cargo_entries = raw_data.get("cargoquery", [])
        for entry in cargo_entries:
            title_data = entry.get("title", {})
            monsters.append(MonsterStats.from_cargo(title_data))
        return monsters

    def format_batch_title_where(self, names: List[str]) -> str:
        escaped_names = []
        for name in names:
            clean_name = name.replace("'", "\\'")
            escaped_names.append(f"'{clean_name}'")
        return f"name IN ({','.join(escaped_names)})"
