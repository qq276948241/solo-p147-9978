import random
from .entities import Player
from .cards import Card, random_cards


class RestEvent:
    def __init__(self, player: Player):
        self.player = player
        self.options = ["休息 (恢复30%最大生命)", "升级 (暂未实现)"]

    def choose(self, index: int) -> str:
        if index == 0:
            amount = int(self.player.max_hp * 0.3)
            healed = self.player.heal(amount)
            return f"你在篝火旁休息，恢复了{healed}点生命"
        return "升级功能暂未实现"


class TreasureEvent:
    def __init__(self, player: Player):
        self.player = player
        self.gold = random.randint(20, 50)
        self.card = random_cards(1)[0]
        self.claimed = False

    def claim(self) -> str:
        if self.claimed:
            return "宝箱已被开启"
        self.player.gold += self.gold
        self.player.add_card(self.card)
        self.claimed = True
        return f"你打开了宝箱，获得{self.gold}金币和卡牌【{self.card.name}】"


class ShopEvent:
    def __init__(self, player: Player):
        self.player = player
        self.cards: list[tuple[Card, int]] = []
        for c in random_cards(5):
            price = c.cost * 20 + random.randint(10, 30)
            self.cards.append((c, price))
        self.heal_price = 30
        self.remove_price = 50

    def buy_card(self, index: int) -> str:
        if index < 0 or index >= len(self.cards):
            return "无效的选择"
        card, price = self.cards[index]
        if price is None:
            return "该卡牌已被购买"
        if self.player.gold < price:
            return "金币不足"
        self.player.gold -= price
        self.player.add_card(card)
        self.cards[index] = (card, None)
        return f"你购买了【{card.name}】"

    def buy_heal(self) -> str:
        if self.player.gold < self.heal_price:
            return "金币不足"
        if self.player.hp >= self.player.max_hp:
            return "生命值已满"
        self.player.gold -= self.heal_price
        healed = self.player.heal(20)
        return f"你花费{self.heal_price}金币，恢复了{healed}点生命"


class CardRewardEvent:
    def __init__(self, player: Player):
        self.player = player
        self.choices = random_cards(3)
        self.selected: Card | None = None

    def choose(self, index: int) -> str:
        if index < 0 or index >= len(self.choices):
            return "无效的选择"
        card = self.choices[index]
        self.player.add_card(card)
        self.selected = card
        return f"你将【{card.name}】加入了卡组"

    def skip(self) -> str:
        self.selected = None
        return "你跳过了卡牌奖励"
