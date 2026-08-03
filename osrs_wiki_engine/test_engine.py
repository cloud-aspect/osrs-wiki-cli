"""
Unit tests for OSRS Wiki Engine (Cargo client, SQLite cache, Models).
"""
import unittest
from osrs_wiki_engine.models import ItemStats, MonsterStats
from osrs_wiki_engine.cache import SQLiteCache
from osrs_wiki_engine.cargo_client import MediaWikiCargoClient

class TestOSRSWikiEngine(unittest.TestCase):

    def test_item_stats_parsing(self):
        mock_cargo_item = {
            "id": "4151",
            "name": "Abyssal whip",
            "members": "1",
            "equipment_slot": "weapon",
            "attack_speed": "4",
            "high_alch": "72000"
        }
        item = ItemStats.from_cargo(mock_cargo_item)
        self.assertEqual(item.id, 4151)
        self.assertEqual(item.name, "Abyssal whip")
        self.assertTrue(item.members)
        self.assertEqual(item.equipment_slot, "weapon")
        self.assertEqual(item.attack_speed, 4)
        self.assertEqual(item.high_alch, 72000)

    def test_monster_stats_parsing(self):
        mock_cargo_monster = {
            "name": "Abyssal Sire",
            "combat_level": "350",
            "hitpoints": "400",
            "max_hit": "30",
            "slayer_req": "85",
            "attack_style": "Melee, Ranged"
        }
        monster = MonsterStats.from_cargo(mock_cargo_monster)
        self.assertEqual(monster.name, "Abyssal Sire")
        self.assertEqual(monster.combat_level, 350)
        self.assertEqual(monster.hitpoints, 400)
        self.assertEqual(monster.slayer_level, 85)

    def test_sqlite_cache_hit_and_expiry(self):
        cache = SQLiteCache(":memory:")
        key = "query_test_key"
        payload = {"cargoquery": [{"title": {"id": "1234", "name": "Dragon dagger"}}]}

        cache.set(key, payload)
        retrieved = cache.get(key, max_age_seconds=60)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved["cargoquery"][0]["title"]["name"], "Dragon dagger")

        # Expiry test
        expired = cache.get(key, max_age_seconds=-1)
        self.assertIsNone(expired)

    def test_cargo_url_construction(self):
        client = MediaWikiCargoClient()
        url = client.build_cargo_query_url(
            tables="Items",
            fields="id,name,attack_speed",
            where="name='Abyssal whip'"
        )
        self.assertIn("action=cargoquery", url)
        self.assertIn("tables=Items", url)
        self.assertIn("where=name%3D%27Abyssal+whip%27", url)

    def test_batch_where_formatting(self):
        client = MediaWikiCargoClient()
        names = ["Abyssal whip", "Dragon dagger", "Twisted bow"]
        where_clause = client.format_batch_title_where(names)
        self.assertEqual(where_clause, "name IN ('Abyssal whip','Dragon dagger','Twisted bow')")

if __name__ == "__main__":
    unittest.main()
