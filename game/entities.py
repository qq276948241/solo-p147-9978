import random
from dataclasses import dataclass, field
from enum import Enum
from .cards import Card, create_starting_deck, shuffle, StatusType


@dataclass
class StatusEffect:
    status_type: StatusType
    duration: int
    value: int = 0
    
    def display(self) -> str:
        icon = self.status_type.icon
        if self.status_type in (StatusType.POISON, StatusType.BURN):
            return f"{icon}{self.value}({self.duration})"
        return f"{icon}({self.duration})"


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
    statuses: list[StatusEffect] = field(default_factory=list)

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
        elif roll < 0.95:
            self.next_action = "毒击"
            self.next_value = random.randint(3, 6) + difficulty
            self.is_defending = False
        else:
            self.next_action = "防御"
            self.next_value = random.randint(5, 10) + difficulty
            self.is_defending = True

    def add_status(self, status_type: StatusType, duration: int, value: int = 0) -> str:
        existing = next((s for s in self.statuses if s.status_type == status_type), None)
        if existing:
            if status_type in (StatusType.POISON, StatusType.BURN):
                existing.value += value
                existing.duration = max(existing.duration, duration)
            else:
                existing.duration = max(existing.duration, duration)
        else:
            self.statuses.append(StatusEffect(status_type, duration, value))
        return f"{self.name}获得{status_type.name}状态"

    def get_attack_multiplier(self) -> float:
        mult = 1.0
        for s in self.statuses:
            if s.status_type == StatusType.WEAK:
                mult *= 0.5
        return mult

    def tick_statuses(self) -> list[str]:
        messages = []
        to_remove = []
        for s in self.statuses:
            if s.status_type == StatusType.POISON:
                dmg = self.take_damage(s.value)
                messages.append(f"{self.name}因中毒受到{dmg}点伤害")
            elif s.status_type == StatusType.BURN:
                dmg = self.take_damage(s.value)
                messages.append(f"{self.name}因燃烧受到{dmg}点伤害")
                s.value += 3
            s.duration -= 1
            if s.duration <= 0:
                to_remove.append(s)
        for s in to_remove:
            self.statuses.remove(s)
        return messages

    def take_damage(self, damage: int) -> int:
        actual = max(0, damage)
        self.hp = max(0, self.hp - actual)
        return actual

    def is_alive(self) -> bool:
        return self.hp > 0

    def intent_display(self) -> str:
        if self.next_action in ("攻击", "重击"):
            dmg = int(self.next_value * self.get_attack_multiplier())
            return f"{self.next_action}{dmg}"
        elif self.next_action == "毒击":
            return f"毒击{self.next_value}"
        elif self.next_action == "防御":
            return f"防御+{self.next_value}"
        return "???"

    def status_display(self) -> str:
        return " ".join(s.display() for s in self.statuses) if self.statuses else ""


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
    statuses: list[StatusEffect] = field(default_factory=list)

    def start_battle(self):
        self.block = 0
        self.energy = self.max_energy
        self.draw_pile = shuffle(self.deck.copy())
        self.discard_pile = []
        self.hand = []
        self.statuses = []
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

    def add_status(self, status_type: StatusType, duration: int, value: int = 0) -> str:
        existing = next((s for s in self.statuses if s.status_type == status_type), None)
        if existing:
            if status_type in (StatusType.POISON, StatusType.BURN, StatusType.STRENGTH):
                existing.value += value
                existing.duration = max(existing.duration, duration) if status_type != StatusType.STRENGTH else existing.duration + duration
            else:
                existing.duration = max(existing.duration, duration)
        else:
            self.statuses.append(StatusEffect(status_type, duration, value))
        return f"你获得{status_type.display_name}状态"

    def get_damage_multiplier(self) -> float:
        mult = 1.0
        for s in self.statuses:
            if s.status_type == StatusType.STRENGTH:
                mult *= (1 + s.value * 0.5)
        return mult

    def tick_statuses(self) -> list[str]:
        messages = []
        to_remove = []
        for s in self.statuses:
            if s.status_type == StatusType.POISON:
                dmg = self.take_damage(s.value)
                messages.append(f"你因中毒受到{dmg}点伤害")
            elif s.status_type == StatusType.BURN:
                dmg = self.take_damage(s.value)
                messages.append(f"你因燃烧受到{dmg}点伤害")
                s.value += 3
            s.duration -= 1
            if s.duration <= 0:
                to_remove.append(s)
        for s in to_remove:
            self.statuses.remove(s)
        return messages

    def play_card(self, index: int, enemies: list[Enemy]) -> tuple[bool, str]:
        if index < 0 or index >= len(self.hand):
            return False, "无效的卡牌序号"
        card = self.hand[index]
        if card.cost > self.energy:
            return False, "能量不足"
        
        self.energy -= card.cost
        self.hand.pop(index)
        self.discard_pile.append(card)

        msg_parts = []
        if card.card_type.value == "attack":
            target = next((e for e in enemies if e.is_alive()), None)
            if target:
                base_dmg = card.value
                dmg = int(base_dmg * self.get_damage_multiplier())
                actual = target.take_damage(dmg)
                msg_parts.append(f"你使用{card.name}，对{target.name}造成{actual}点伤害")
        elif card.card_type.value == "defense":
            self.block += card.value
            msg_parts.append(f"你使用{card.name}，获得{card.value}点护甲")
        elif card.card_type.value == "heal":
            healed = min(card.value, self.max_hp - self.hp)
            self.hp += healed
            msg_parts.append(f"你使用{card.name}，恢复{healed}点生命")
        
        if card.applies_status:
            target = next((e for e in enemies if e.is_alive()), None)
            if target and card.status_target == "enemy":
                status_msg = target.add_status(card.status_type, card.status_duration, card.status_value)
                msg_parts.append(status_msg)
            elif card.status_target == "self":
                status_msg = self.add_status(card.status_type, card.status_duration, card.status_value)
                msg_parts.append(status_msg)
        
        return True, "，".join(msg_parts)

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

    def status_display(self) -> str:
        return " ".join(s.display() for s in self.statuses) if self.statuses else ""


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
