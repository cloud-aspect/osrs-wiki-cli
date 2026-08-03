"""
Strongly-typed data models for OSRS Cargo tables.
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

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
            id=int(cargo_dict.get("id", 0)),
            name=cargo_dict.get("name", "Unknown"),
            members=str(cargo_dict.get("members", "0")).lower() in ("1", "true", "yes"),
            equipment_slot=cargo_dict.get("equipment_slot"),
            attack_speed=int(cargo_dict["attack_speed"]) if cargo_dict.get("attack_speed") else None,
            high_alch=int(cargo_dict["high_alch"]) if cargo_dict.get("high_alch") else None
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
            combat_level=int(cargo_dict.get("combat_level", 0)),
            hitpoints=int(cargo_dict.get("hitpoints", 0)),
            max_hit=int(cargo_dict.get("max_hit", 0)),
            slayer_level=int(cargo_dict.get("slayer_req", 0) or 0),
            attack_style=cargo_dict.get("attack_style")
        )

@dataclass
class DropTableEntry:
    item_name: str
    monster_name: str
    rarity: str
    quantity: str
    fractional_rate: Optional[float] = None
