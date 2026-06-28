import random
from dataclasses import dataclass, field
from enum import Enum
from .cards import Card, create_starting_deck, shuffle


class NodeType(Enum):
    BATTLE = "battle"
    REST = "rest"
    TREASURE = "treasure"
    SHOP = "shop"
    BOSS = "boss"
    START = "start"


@dataclass
class Enemy:
    name: str
    max_hp: int
    hp: int
    next_action: str = ""
    next_value: int = 0
    is_defending: bool = False

    def plan_action(self, difficulty: int = 1):
        roll = random.random()
        if roll < 0.6:
            self.next_action = "攻击"
            self.next_value = random.randint(4, 8) + difficulty * 2
            self.is_defending = False
        elif roll < 0.85:
            self.next_action = "重击"
            self.next_value = random.randint(10, 15) + difficulty * 3
            self.is_defending = False
        else:
            self.next_action = "防御"
            self.next_value = random.randint(5, 10) + difficulty
            self.is_defending = True

    def take_damage(self, damage: int) -> int:
        actual = max(0, damage)
        self.hp = max(0, self.hp - actual)
        return actual

    def is_alive(self) -> bool:
        return self.hp > 0

    def intent_display(self) -> str:
        if self.next_action == "攻击" or self.next_action == "重击":
            return f"{self.next_action}{self.next_value}"
        elif self.next_action == "防御":
            return f"防御+{self.next_value}"
        return "???"


def create_enemies(floor: int, is_boss: bool = False) -> list[Enemy]:
    if is_boss:
        if floor <= 2:
            return [Enemy("哥布林首领", 50, 50)]
        elif floor <= 4:
            return [Enemy("黑暗骑士", 80, 80)]
        else:
            return [Enemy("魔龙", 120, 120)]
    
    difficulty = floor
    enemy_pool = [
        Enemy("史莱姆", 15 + difficulty * 3, 15 + difficulty * 3),
        Enemy("哥布林", 20 + difficulty * 3, 20 + difficulty * 3),
        Enemy("骷髅兵", 25 + difficulty * 3, 25 + difficulty * 3),
    ]
    
    count = 1 if floor == 1 else random.randint(1, min(2, floor))
    result = []
    for _ in range(count):
        template = random.choice(enemy_pool)
        result.append(Enemy(template.name, template.max_hp, template.max_hp))
    return result


@dataclass
class Player:
    max_hp: int = 60
    hp: int = 60
    block: int = 0
    energy: int = 3
    max_energy: int = 3
    gold: int = 50
    deck: list[Card] = field(default_factory=create_starting_deck)
    draw_pile: list[Card] = field(default_factory=list)
    discard_pile: list[Card] = field(default_factory=list)
    hand: list[Card] = field(default_factory=list)

    def start_battle(self):
        self.block = 0
        self.energy = self.max_energy
        self.draw_pile = shuffle(self.deck.copy())
        self.discard_pile = []
        self.hand = []
        self.draw_cards(5)

    def draw_cards(self, count: int):
        for _ in range(count):
            if not self.draw_pile:
                if not self.discard_pile:
                    return
                self.draw_pile = shuffle(self.discard_pile)
                self.discard_pile = []
            if self.draw_pile:
                self.hand.append(self.draw_pile.pop())

    def play_card(self, index: int, enemies: list[Enemy]) -> tuple[bool, str]:
        if index < 0 or index >= len(self.hand):
            return False, "无效的卡牌序号"
        card = self.hand[index]
        if card.cost > self.energy:
            return False, "能量不足"
        
        self.energy -= card.cost
        self.hand.pop(index)
        self.discard_pile.append(card)

        msg = ""
        if card.card_type.value == "attack":
            target = next((e for e in enemies if e.is_alive()), None)
            if target:
                dmg = target.take_damage(card.value)
                msg = f"你使用{card.name}，对{target.name}造成{dmg}点伤害"
        elif card.card_type.value == "defense":
            self.block += card.value
            msg = f"你使用{card.name}，获得{card.value}点护甲"
        elif card.card_type.value == "heal":
            healed = min(card.value, self.max_hp - self.hp)
            self.hp += healed
            msg = f"你使用{card.name}，恢复{healed}点生命"
        
        return True, msg

    def take_damage(self, damage: int) -> int:
        remaining = damage
        if self.block > 0:
            absorbed = min(self.block, remaining)
            self.block -= absorbed
            remaining -= absorbed
        if remaining > 0:
            self.hp = max(0, self.hp - remaining)
        return remaining

    def end_turn_discard(self):
        self.discard_pile.extend(self.hand)
        self.hand = []

    def is_alive(self) -> bool:
        return self.hp > 0

    def add_card(self, card: Card):
        self.deck.append(card)

    def heal(self, amount: int) -> int:
        healed = min(amount, self.max_hp - self.hp)
        self.hp += healed
        return healed


@dataclass
class MapNode:
    node_type: NodeType
    floor: int
    index: int
    connections: list[int] = field(default_factory=list)
    visited: bool = False

    def display(self) -> str:
        icons = {
            NodeType.BATTLE: "⚔",
            NodeType.REST: "🔥",
            NodeType.TREASURE: "📦",
            NodeType.SHOP: "🛒",
            NodeType.BOSS: "👑",
            NodeType.START: "🚩",
        }
        names = {
            NodeType.BATTLE: "战斗",
            NodeType.REST: "休息",
            NodeType.TREASURE: "宝箱",
            NodeType.SHOP: "商店",
            NodeType.BOSS: "BOSS",
            NodeType.START: "起点",
        }
        return f"{icons[self.node_type]} {names[self.node_type]}"
