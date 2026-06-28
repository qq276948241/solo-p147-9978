from .entities import Player, Enemy, create_enemies
from .cards import Card


class BattleState:
    PLAYER_TURN = "player_turn"
    ENEMY_TURN = "enemy_turn"
    VICTORY = "victory"
    DEFEAT = "defeat"


class Battle:
    def __init__(self, player: Player, floor: int, is_boss: bool = False):
        self.player = player
        self.enemies = create_enemies(floor, is_boss)
        self.turn = 1
        self.state = BattleState.PLAYER_TURN
        self.log: list[str] = []
        self.floor = floor
        self.is_boss = is_boss
        self._start()

    def _start(self):
        self.player.start_battle()
        for enemy in self.enemies:
            enemy.plan_action(self.floor)
        self.log.append(f"=== 第{self.floor}层战斗开始 ===")
        if self.is_boss:
            self.log.append("【BOSS战】")
        self.log.append(f"你遭遇了: {', '.join(e.name for e in self.enemies)}")

    def play_card(self, hand_index: int) -> tuple[bool, str]:
        if self.state != BattleState.PLAYER_TURN:
            return False, "不是你的回合"
        success, msg = self.player.play_card(hand_index, self.enemies)
        if success:
            self.log.append(msg)
            self._check_victory()
        return success, msg

    def end_turn(self):
        if self.state != BattleState.PLAYER_TURN:
            return
        self.player.end_turn_discard()
        self.player.block = 0
        self.state = BattleState.ENEMY_TURN
        self.log.append("--- 敌人回合 ---")
        self._enemy_turn()

    def _enemy_turn(self):
        for enemy in self.enemies:
            if not enemy.is_alive():
                continue
            if enemy.next_action == "攻击" or enemy.next_action == "重击":
                dmg = self.player.take_damage(enemy.next_value)
                self.log.append(f"{enemy.name}使用{enemy.next_action}，对你造成{dmg}点伤害")
                if not self.player.is_alive():
                    self.state = BattleState.DEFEAT
                    self.log.append("=== 你被击败了 ===")
                    return
            elif enemy.next_action == "防御":
                self.log.append(f"{enemy.name}进行防御，获得{enemy.next_value}点护甲")
        if not self.player.is_alive():
            return
        self._next_player_turn()

    def _next_player_turn(self):
        self.turn += 1
        self.player.energy = self.player.max_energy
        self.player.draw_cards(5)
        for enemy in self.enemies:
            if enemy.is_alive():
                enemy.plan_action(self.floor)
        self.state = BattleState.PLAYER_TURN
        self.log.append(f"--- 第{self.turn}回合 ---")

    def _check_victory(self):
        if all(not e.is_alive() for e in self.enemies):
            self.state = BattleState.VICTORY
            gold_reward = 15 + self.floor * 5 + (20 if self.is_boss else 0)
            self.player.gold += gold_reward
            self.log.append(f"=== 胜利！获得{gold_reward}金币 ===")

    def is_over(self) -> bool:
        return self.state in (BattleState.VICTORY, BattleState.DEFEAT)

    def is_victory(self) -> bool:
        return self.state == BattleState.VICTORY
