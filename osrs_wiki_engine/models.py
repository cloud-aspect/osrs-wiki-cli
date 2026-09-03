"""
Strongly-typed data models for OSRS Cargo tables.
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

def _safe_int(val: Any, default: Optional[int] = None) -> Optional[int]:
    if val is None or str(val).strip() == "":
        return default
    try:
        return int(val)
    except (ValueError, TypeError):
        return default

@dataclass
class ItemStats:
    id: int
    name: str
    members: bool
    equipment_slot: Optional[str] = None
    attack_speed: Optional[int] = None
    high_alch: Optional[int] = None

    @classmethod
    def from_cargo(cls, cargo_dict: Dict[str, Any]) -> "ItemStats":
        return cls(
            id=_safe_int(cargo_dict.get("id"), default=0),
            name=cargo_dict.get("name", "Unknown"),
            members=str(cargo_dict.get("members", "0")).lower() in ("1", "true", "yes"),
            equipment_slot=cargo_dict.get("equipment_slot"),
            attack_speed=_safe_int(cargo_dict.get("attack_speed")),
            high_alch=_safe_int(cargo_dict.get("high_alch"))
        )

@dataclass
class MonsterStats:
    name: str
    combat_level: int
    hitpoints: int
    max_hit: int
    slayer_level: int = 0
    attack_style: Optional[str] = None

    @classmethod
    def from_cargo(cls, cargo_dict: Dict[str, Any]) -> "MonsterStats":
        return cls(
            name=cargo_dict.get("name", "Unknown"),
            combat_level=_safe_int(cargo_dict.get("combat_level"), default=0),
            hitpoints=_safe_int(cargo_dict.get("hitpoints"), default=0),
            max_hit=_safe_int(cargo_dict.get("max_hit"), default=0),
            slayer_level=_safe_int(cargo_dict.get("slayer_req"), default=0),
            attack_style=cargo_dict.get("attack_style")
        )

@dataclass
class DropTableEntry:
    item_name: str
    monster_name: str
    rarity: str
    quantity: str
    fractional_rate: Optional[float] = None
