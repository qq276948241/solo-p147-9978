import random
from dataclasses import dataclass, field
from enum import Enum


class StatusType(Enum):
    POISON = "poison"
    WEAK = "weak"
    BURN = "burn"
    STRENGTH = "strength"
    THORNS = "thorns"

    @property
    def icon(self) -> str:
        return {
            StatusType.POISON: "☠",
            StatusType.WEAK: "💫",
            StatusType.BURN: "🔥",
            StatusType.STRENGTH: "💪",
            StatusType.THORNS: "🌵",
        }[self]

    @property
    def display_name(self) -> str:
        return {
            StatusType.POISON: "中毒",
            StatusType.WEAK: "虚弱",
            StatusType.BURN: "燃烧",
            StatusType.STRENGTH: "力量",
            StatusType.THORNS: "荆棘",
        }[self]

    @property
    def color_index(self) -> int:
        return {
            StatusType.POISON: 8,
            StatusType.WEAK: 9,
            StatusType.BURN: 10,
            StatusType.STRENGTH: 11,
            StatusType.THORNS: 12,
        }[self]

    @property
    def is_debuff(self) -> bool:
        return self in (StatusType.POISON, StatusType.WEAK, StatusType.BURN)


class CardType(Enum):
    ATTACK = "attack"
    DEFENSE = "defense"
    HEAL = "heal"


@dataclass
class Card:
    name: str
    card_type: CardType
    cost: int
    value: int
    description: str
    applies_status: bool = False
    status_type: StatusType | None = None
    status_value: int = 0
    status_duration: int = 0
    status_target: str = "enemy"

    def display(self) -> str:
        type_icon = {
            CardType.ATTACK: "⚔",
            CardType.DEFENSE: "🛡",
            CardType.HEAL: "❤",
        }[self.card_type]
        base = f"[{self.cost}] {type_icon} {self.name}({self.value})"
        if self.applies_status and self.status_type:
            base += f" {self.status_type.icon}"
        return base


CARD_TEMPLATES = [
    Card("打击", CardType.ATTACK, 1, 6, "造成6点伤害"),
    Card("重击", CardType.ATTACK, 2, 12, "造成12点伤害"),
    Card("猛击", CardType.ATTACK, 2, 10, "造成10点伤害"),
    Card("致命一击", CardType.ATTACK, 3, 15, "造成15点伤害"),
    Card("快斩", CardType.ATTACK, 1, 8, "造成8点伤害"),
    Card("防御", CardType.DEFENSE, 1, 6, "获得6点护甲"),
    Card("铁壁", CardType.DEFENSE, 2, 12, "获得12点护甲"),
    Card("护盾术", CardType.DEFENSE, 1, 5, "获得5点护甲"),
    Card("坚守", CardType.DEFENSE, 2, 10, "获得10点护甲"),
    Card("治疗", CardType.HEAL, 1, 6, "恢复6点生命"),
    Card("强效治疗", CardType.HEAL, 2, 12, "恢复12点生命"),
    Card("小回血", CardType.HEAL, 1, 4, "恢复4点生命"),
    Card("毒刃", CardType.ATTACK, 1, 4, "造成4伤害，使敌人中毒(5/3回合)",
         applies_status=True, status_type=StatusType.POISON, status_value=5, status_duration=3),
    Card("剧毒", CardType.ATTACK, 2, 0, "使敌人中毒(8/4回合)",
         applies_status=True, status_type=StatusType.POISON, status_value=8, status_duration=4),
    Card("虚弱打击", CardType.ATTACK, 1, 5, "造成5伤害，使敌人虚弱(2回合)",
         applies_status=True, status_type=StatusType.WEAK, status_value=0, status_duration=2),
    Card("燃火术", CardType.ATTACK, 1, 3, "造成3伤害，使敌人燃烧(4/3回合)",
         applies_status=True, status_type=StatusType.BURN, status_value=4, status_duration=3),
    Card("烈焰爆发", CardType.ATTACK, 2, 8, "造成8伤害，使敌人燃烧(6/3回合)",
         applies_status=True, status_type=StatusType.BURN, status_value=6, status_duration=3),
    Card("力量药剂", CardType.ATTACK, 1, 0, "获得力量(1/3回合，增伤50%)",
         applies_status=True, status_type=StatusType.STRENGTH, status_value=1, status_duration=3, status_target="self"),
    Card("狂暴", CardType.ATTACK, 2, 0, "获得力量(2/4回合，每层增伤50%)",
         applies_status=True, status_type=StatusType.STRENGTH, status_value=2, status_duration=4, status_target="self"),
    Card("荆棘护甲", CardType.DEFENSE, 2, 8, "获得8护甲，获得荆棘(3/3回合)",
         applies_status=True, status_type=StatusType.THORNS, status_value=3, status_duration=3, status_target="self"),
]


def create_starting_deck() -> list[Card]:
    deck = []
    for _ in range(4):
        deck.append(Card("打击", CardType.ATTACK, 1, 6, "造成6点伤害"))
    for _ in range(3):
        deck.append(Card("防御", CardType.DEFENSE, 1, 5, "获得5点护甲"))
    deck.append(Card("治疗", CardType.HEAL, 1, 5, "恢复5点生命"))
    return deck


def random_cards(count: int = 3) -> list[Card]:
    return random.sample([Card(c.name, c.card_type, c.cost, c.value, c.description)
                          for c in CARD_TEMPLATES], count)


def shuffle(cards: list[Card]) -> list[Card]:
    result = cards.copy()
    random.shuffle(result)
    return result
