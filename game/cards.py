import random
from dataclasses import dataclass, field
from enum import Enum


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

    def display(self) -> str:
        type_icon = {
            CardType.ATTACK: "⚔",
            CardType.DEFENSE: "🛡",
            CardType.HEAL: "❤",
        }[self.card_type]
        return f"[{self.cost}] {type_icon} {self.name}({self.value})"


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
