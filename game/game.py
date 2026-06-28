from enum import Enum
from .entities import Player, MapNode, NodeType
from .map_gen import generate_map, TOTAL_FLOORS
from .battle import Battle, BattleState
from .events import RestEvent, TreasureEvent, ShopEvent, CardRewardEvent


class GameScene(Enum):
    MAP = "map"
    BATTLE = "battle"
    CARD_REWARD = "card_reward"
    REST = "rest"
    TREASURE = "treasure"
    SHOP = "shop"
    GAME_OVER = "game_over"
    VICTORY = "victory"


class Game:
    def __init__(self):
        self.player = Player()
        self.map = generate_map()
        self.current_floor = 0
        self.current_node_idx = 0
        self.selected_floor = 0
        self.selected_node_idx = 0
        self.scene = GameScene.MAP
        self.battle: Battle | None = None
        self.card_reward: CardRewardEvent | None = None
        self.rest_event: RestEvent | None = None
        self.treasure_event: TreasureEvent | None = None
        self.shop_event: ShopEvent | None = None
        self.log: list[str] = ["欢迎来到卡牌爬塔！使用 WASD 选择路径，回车确认。"]
        self.final_message = ""
        self._init_map_selection()

    def _init_map_selection(self):
        self.selected_floor = 1
        current_node = self.map[self.current_floor][self.current_node_idx]
        if current_node.connections:
            self.selected_node_idx = current_node.connections[0]

    def log_msg(self, msg: str):
        self.log.append(msg)
        if len(self.log) > 50:
            self.log = self.log[-50:]

    def move_map_selection(self, direction: str):
        if self.scene != GameScene.MAP:
            return
        current_node = self.map[self.current_floor][self.current_node_idx]
        next_floor = self.current_floor + 1
        if next_floor >= len(self.map):
            return
        
        available = current_node.connections
        if direction == "left" or direction == "up":
            if self.selected_node_idx > min(available):
                self.selected_node_idx -= 1
                while self.selected_node_idx not in available and self.selected_node_idx > min(available):
                    self.selected_node_idx -= 1
        elif direction == "right" or direction == "down":
            if self.selected_node_idx < max(available):
                self.selected_node_idx += 1
                while self.selected_node_idx not in available and self.selected_node_idx < max(available):
                    self.selected_node_idx += 1

    def confirm_map_selection(self):
        if self.scene != GameScene.MAP:
            return
        current_node = self.map[self.current_floor][self.current_node_idx]
        if self.selected_node_idx not in current_node.connections:
            return
        
        self.current_floor += 1
        self.current_node_idx = self.selected_node_idx
        target_node = self.map[self.current_floor][self.current_node_idx]
        target_node.visited = True
        self._enter_node(target_node)

    def _enter_node(self, node: MapNode):
        if node.node_type == NodeType.BATTLE:
            self.battle = Battle(self.player, self.current_floor, is_boss=False)
            self.scene = GameScene.BATTLE
            self.log.extend(self.battle.log)
        elif node.node_type == NodeType.BOSS:
            self.battle = Battle(self.player, self.current_floor, is_boss=True)
            self.scene = GameScene.BATTLE
            self.log.extend(self.battle.log)
        elif node.node_type == NodeType.REST:
            self.rest_event = RestEvent(self.player)
            self.scene = GameScene.REST
            self.log_msg("你来到了休息点")
        elif node.node_type == NodeType.TREASURE:
            self.treasure_event = TreasureEvent(self.player)
            self.scene = GameScene.TREASURE
            self.log_msg("你发现了一个宝箱")
        elif node.node_type == NodeType.SHOP:
            self.shop_event = ShopEvent(self.player)
            self.scene = GameScene.SHOP
            self.log_msg("你来到了商店")

    def battle_play_card(self, hand_index: int):
        if self.scene != GameScene.BATTLE or not self.battle:
            return
        success, msg = self.battle.play_card(hand_index)
        if success:
            self.log.append(msg)
            if self.battle.is_over():
                self._handle_battle_end()
        else:
            self.log_msg(msg)

    def battle_end_turn(self):
        if self.scene != GameScene.BATTLE or not self.battle:
            return
        self.battle.end_turn()
        self.log.extend(self.battle.log[-10:])
        if self.battle.is_over():
            self._handle_battle_end()

    def _handle_battle_end(self):
        if not self.battle:
            return
        if self.battle.state == BattleState.VICTORY:
            if self.current_floor == TOTAL_FLOORS:
                self.final_message = f"恭喜通关！你到达了第{self.current_floor}层并击败了最终BOSS！"
                self.scene = GameScene.VICTORY
            else:
                self.card_reward = CardRewardEvent(self.player)
                self.scene = GameScene.CARD_REWARD
                self.log_msg("战斗胜利！从三张卡牌中选择一张加入卡组")
        elif self.battle.state == BattleState.DEFEAT:
            self.final_message = f"游戏结束！你爬到了第{self.current_floor}层。"
            self.scene = GameScene.GAME_OVER

    def choose_card_reward(self, index: int):
        if self.scene != GameScene.CARD_REWARD or not self.card_reward:
            return
        msg = self.card_reward.choose(index)
        self.log_msg(msg)
        self._return_to_map()

    def skip_card_reward(self):
        if self.scene != GameScene.CARD_REWARD or not self.card_reward:
            return
        msg = self.card_reward.skip()
        self.log_msg(msg)
        self._return_to_map()

    def choose_rest(self, index: int):
        if self.scene != GameScene.REST or not self.rest_event:
            return
        msg = self.rest_event.choose(index)
        self.log_msg(msg)
        self._return_to_map()

    def claim_treasure(self):
        if self.scene != GameScene.TREASURE or not self.treasure_event:
            return
        msg = self.treasure_event.claim()
        self.log_msg(msg)
        self._return_to_map()

    def shop_buy_card(self, index: int):
        if self.scene != GameScene.SHOP or not self.shop_event:
            return
        msg = self.shop_event.buy_card(index)
        self.log_msg(msg)

    def shop_buy_heal(self):
        if self.scene != GameScene.SHOP or not self.shop_event:
            return
        msg = self.shop_event.buy_heal()
        self.log_msg(msg)

    def leave_shop(self):
        if self.scene != GameScene.SHOP:
            return
        self._return_to_map()

    def _return_to_map(self):
        self.scene = GameScene.MAP
        self.battle = None
        self.card_reward = None
        self.rest_event = None
        self.treasure_event = None
        self.shop_event = None
        if self.current_floor < len(self.map) - 1:
            self.selected_floor = self.current_floor + 1
            current_node = self.map[self.current_floor][self.current_node_idx]
            if current_node.connections:
                self.selected_node_idx = current_node.connections[0]
