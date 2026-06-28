import curses
from .game import Game, GameScene
from .entities import NodeType
from .battle import BattleState
from .cards import CardType


LEFT_PANEL_WIDTH = 28


def draw_player_panel(stdscr, game: Game, y: int, x: int, h: int, w: int):
    player = game.player
    stdscr.attron(curses.color_pair(1))
    for i in range(h):
        stdscr.addstr(y + i, x, " " * w)
    stdscr.attroff(curses.color_pair(1))
    
    stdscr.addstr(y, x, "═══ 玩家状态 ═══".center(w), curses.color_pair(2) | curses.A_BOLD)
    
    line = y + 2
    stdscr.addstr(line, x + 1, f"❤ 生命: {player.hp}/{player.max_hp}")
    hp_bar_len = w - 8
    filled = int(player.hp / player.max_hp * hp_bar_len)
    stdscr.addstr(line + 1, x + 1, "[" + "█" * filled + "░" * (hp_bar_len - filled) + "]", curses.color_pair(3))
    
    line += 3
    stdscr.addstr(line, x + 1, f"💰 金币: {player.gold}")
    
    line += 2
    stdscr.addstr(line, x + 1, f"🗺 层数: {game.current_floor}/5")
    
    line += 2
    stdscr.addstr(line, x + 1, "═══ 卡组信息 ═══", curses.color_pair(2))
    line += 1
    stdscr.addstr(line, x + 1, f"卡组: {len(player.deck)}张")
    if game.scene == GameScene.BATTLE and game.battle:
        line += 1
        stdscr.addstr(line, x + 1, f"抽牌堆: {len(player.draw_pile)}")
        line += 1
        stdscr.addstr(line, x + 1, f"弃牌堆: {len(player.discard_pile)}")
        line += 1
        stdscr.addstr(line, x + 1, f"⚡ 能量: {player.energy}/{player.max_energy}")
        line += 1
        stdscr.addstr(line, x + 1, f"🛡 护甲: {player.block}")

    for i in range(h):
        stdscr.addstr(y + i, x + w - 1, "│")
    for j in range(w):
        stdscr.addstr(y + h - 1, x + j, "═")


def draw_map_center(stdscr, game: Game, y: int, x: int, h: int, w: int):
    stdscr.addstr(y, x, "═══ 地图 ═══".center(w), curses.color_pair(2) | curses.A_BOLD)
    
    floor_start_y = y + 2
    floor_h = (h - 3) // 6
    current_node = game.map[game.current_floor][game.current_node_idx]
    
    for floor_idx in range(len(game.map) - 1, -1, -1):
        row_y = floor_start_y + (5 - floor_idx) * floor_h
        if row_y >= y + h - 1:
            continue
        
        nodes = game.map[floor_idx]
        node_spacing = w // (len(nodes) + 1)
        
        for i, node in enumerate(nodes):
            node_x = x + node_spacing * (i + 1) - 5
            display = node.display()
            
            attrs = 0
            is_current = (floor_idx == game.current_floor and i == game.current_node_idx)
            is_selected = (floor_idx == game.current_floor + 1 and i == game.selected_node_idx)
            is_reachable = (floor_idx == game.current_floor + 1 and i in current_node.connections)
            
            if is_current:
                attrs = curses.color_pair(5) | curses.A_BOLD
            elif is_selected:
                attrs = curses.color_pair(4) | curses.A_BOLD | curses.A_REVERSE
            elif node.visited:
                attrs = curses.color_pair(7)
            elif is_reachable:
                attrs = curses.color_pair(4)
            else:
                attrs = curses.color_pair(6)
            
            try:
                stdscr.addstr(row_y, max(x + 1, node_x), display.center(10), attrs)
            except:
                pass
        
        if floor_idx > 0:
            prev_nodes = game.map[floor_idx - 1]
            for pi, pnode in enumerate(prev_nodes):
                px = x + (w // (len(prev_nodes) + 1)) * (pi + 1)
                for ci in pnode.connections:
                    if ci < len(nodes):
                        cx = x + node_spacing * (ci + 1)
                        mid_y = row_y + floor_h // 2
                        line_char = "│"
                        try:
                            if floor_idx - 1 == game.current_floor:
                                stdscr.addstr(mid_y, min(cx, px), line_char, curses.color_pair(4))
                            else:
                                stdscr.addstr(mid_y, min(cx, px), line_char, curses.color_pair(6))
                        except:
                            pass

    help_y = y + h - 3
    stdscr.addstr(help_y, x + 1, " WASD/方向键: 选择路径    Enter: 确认    Q: 退出", curses.color_pair(7))


def draw_battle_center(stdscr, game: Game, y: int, x: int, h: int, w: int):
    if not game.battle:
        return
    
    title = "═══ BOSS战 ═══" if game.battle.is_boss else "═══ 战斗 ═══"
    stdscr.addstr(y, x, title.center(w), curses.color_pair(2) | curses.A_BOLD)
    
    enemies_y = y + 3
    enemy_count = len(game.battle.enemies)
    enemy_width = w // max(1, enemy_count)
    
    for i, enemy in enumerate(game.battle.enemies):
        ex = x + i * enemy_width + 2
        if not enemy.is_alive():
            stdscr.addstr(enemies_y, ex, f"💀 {enemy.name} (已死亡)", curses.color_pair(7))
            continue
        
        intent = enemy.intent_display()
        color = curses.color_pair(4) if "攻击" in intent or "重击" in intent else curses.color_pair(5)
        stdscr.addstr(enemies_y, ex, f"⚠ {intent}", color | curses.A_BOLD)
        stdscr.addstr(enemies_y + 1, ex, f"👹 {enemy.name}")
        
        hp_text = f"HP: {enemy.hp}/{enemy.max_hp}"
        hp_bar_len = min(20, enemy_width - 4)
        filled = int(enemy.hp / enemy.max_hp * hp_bar_len)
        stdscr.addstr(enemies_y + 2, ex, "[" + "█" * filled + "░" * (hp_bar_len - filled) + "]", curses.color_pair(3))
        stdscr.addstr(enemies_y + 3, ex, hp_text)
    
    hand_y = y + h - 10
    stdscr.addstr(hand_y - 1, x + 1, "─" * (w - 2), curses.color_pair(7))
    stdscr.addstr(hand_y, x + 1, "手牌:")
    
    for i, card in enumerate(game.player.hand):
        card_y = hand_y + 1 + (i // 3) * 2
        card_x = x + 1 + (i % 3) * (w // 3)
        if card_y >= y + h - 2:
            continue
        
        can_play = card.cost <= game.player.energy and game.battle.state == BattleState.PLAYER_TURN
        color = curses.color_pair(4) if can_play else curses.color_pair(7)
        
        type_icon = {CardType.ATTACK: "⚔", CardType.DEFENSE: "🛡", CardType.HEAL: "❤"}[card.card_type]
        card_text = f" {i+1}. [{card.cost}] {type_icon}{card.name}({card.value}) "
        
        if can_play:
            stdscr.addstr(card_y, card_x, card_text, color | curses.A_BOLD)
        else:
            stdscr.addstr(card_y, card_x, card_text, color)
    
    turn_info = f"回合 {game.battle.turn}"
    if game.battle.state == BattleState.PLAYER_TURN:
        turn_info += " - 你的回合 (1-5出牌, 空格结束回合)"
    elif game.battle.state == BattleState.ENEMY_TURN:
        turn_info += " - 敌人回合..."
    stdscr.addstr(y + 1, x + 1, turn_info, curses.color_pair(2))


def draw_card_reward_center(stdscr, game: Game, y: int, x: int, h: int, w: int):
    if not game.card_reward:
        return
    
    stdscr.addstr(y, x, "═══ 选择奖励卡牌 ═══".center(w), curses.color_pair(2) | curses.A_BOLD)
    stdscr.addstr(y + 2, x + 1, "选择一张卡牌加入你的卡组 (1-3 选择, S 跳过):".center(w - 2))
    
    card_y = y + 5
    card_w = w // 3
    
    for i, card in enumerate(game.card_reward.choices):
        cx = x + i * card_w + card_w // 2 - 12
        type_icon = {CardType.ATTACK: "⚔", CardType.DEFENSE: "🛡", CardType.HEAL: "❤"}[card.card_type]
        
        stdscr.addstr(card_y, cx, f" {i+1}. [{card.cost}] {type_icon} {card.name} ".center(24), curses.color_pair(4) | curses.A_BOLD)
        stdscr.addstr(card_y + 1, cx, f"  数值: {card.value}".center(24), curses.color_pair(5))
        stdscr.addstr(card_y + 2, cx, f"  {card.description}".center(24), curses.color_pair(7))
        stdscr.addstr(card_y + 3, cx, "─" * 24, curses.color_pair(7))


def draw_event_center(stdscr, game: Game, y: int, x: int, h: int, w: int):
    if game.scene == GameScene.REST and game.rest_event:
        stdscr.addstr(y, x, "═══ 休息点 ═══".center(w), curses.color_pair(2) | curses.A_BOLD)
        stdscr.addstr(y + 3, x + 2, "🔥 篝火旁，你可以选择:".center(w - 4))
        for i, opt in enumerate(game.rest_event.options):
            color = curses.color_pair(4) if i == 0 else curses.color_pair(7)
            stdscr.addstr(y + 5 + i * 2, x + 4, f" {i+1}. {opt}", color | curses.A_BOLD)
    
    elif game.scene == GameScene.TREASURE and game.treasure_event:
        stdscr.addstr(y, x, "═══ 宝箱 ═══".center(w), curses.color_pair(2) | curses.A_BOLD)
        if not game.treasure_event.claimed:
            stdscr.addstr(y + 3, x + 2, "📦 你发现了一个宝箱！".center(w - 4))
            stdscr.addstr(y + 5, x + 2, f"   金币: {game.treasure_event.gold}".center(w - 4), curses.color_pair(3))
            type_icon = {CardType.ATTACK: "⚔", CardType.DEFENSE: "🛡", CardType.HEAL: "❤"}[game.treasure_event.card.card_type]
            stdscr.addstr(y + 6, x + 2, f"   卡牌: {type_icon} {game.treasure_event.card.name}({game.treasure_event.card.value})".center(w - 4), curses.color_pair(4))
            stdscr.addstr(y + 9, x + 2, " 按 Enter 开启宝箱 ".center(w - 4), curses.color_pair(5) | curses.A_BOLD | curses.A_REVERSE)
        else:
            stdscr.addstr(y + 3, x + 2, " 宝箱已开启 ".center(w - 4), curses.color_pair(7))
            stdscr.addstr(y + 5, x + 2, " 按 Enter 返回地图 ".center(w - 4), curses.color_pair(4) | curses.A_BOLD)
    
    elif game.scene == GameScene.SHOP and game.shop_event:
        stdscr.addstr(y, x, "═══ 商店 ═══".center(w), curses.color_pair(2) | curses.A_BOLD)
        stdscr.addstr(y + 2, x + 2, f"💰 你的金币: {game.player.gold}", curses.color_pair(3))
        
        item_y = y + 4
        for i, (card, price) in enumerate(game.shop_event.cards):
            if price is None:
                stdscr.addstr(item_y + i, x + 2, f" {i+1}. [已售出]", curses.color_pair(7))
            else:
                type_icon = {CardType.ATTACK: "⚔", CardType.DEFENSE: "🛡", CardType.HEAL: "❤"}[card.card_type]
                can_buy = game.player.gold >= price
                color = curses.color_pair(4) if can_buy else curses.color_pair(7)
                stdscr.addstr(item_y + i, x + 2, f" {i+1}. [{card.cost}] {type_icon}{card.name}({card.value}) - {price}💰", color | (curses.A_BOLD if can_buy else 0))
        
        heal_y = item_y + 6
        can_heal = game.player.gold >= game.shop_event.heal_price and game.player.hp < game.player.max_hp
        color = curses.color_pair(4) if can_heal else curses.color_pair(7)
        stdscr.addstr(heal_y, x + 2, f" H. 恢复20HP - {game.shop_event.heal_price}💰", color | (curses.A_BOLD if can_heal else 0))
        stdscr.addstr(heal_y + 2, x + 2, " Q. 离开商店", curses.color_pair(5) | curses.A_BOLD)


def draw_end_screen(stdscr, game: Game, y: int, x: int, h: int, w: int):
    is_victory = game.scene == GameScene.VICTORY
    title = "═══ 胜利！ ═══" if is_victory else "═══ 游戏结束 ═══"
    color = curses.color_pair(3) if is_victory else curses.color_pair(4)
    
    stdscr.addstr(y + h // 3, x, title.center(w), color | curses.A_BOLD)
    stdscr.addstr(y + h // 3 + 2, x + 2, game.final_message.center(w - 4), curses.color_pair(2) | curses.A_BOLD)
    
    stats = [
        f"到达层数: {game.current_floor}/5",
        f"最终生命: {game.player.hp}/{game.player.max_hp}",
        f"卡组数量: {len(game.player.deck)}张",
        f"剩余金币: {game.player.gold}",
    ]
    for i, stat in enumerate(stats):
        stdscr.addstr(y + h // 3 + 4 + i, x + 2, stat.center(w - 4), curses.color_pair(7))
    
    stdscr.addstr(y + h - 3, x + 2, " 按 Enter 重新开始 / Q 退出 ".center(w - 4), curses.color_pair(5) | curses.A_BOLD)


def draw_log(stdscr, game: Game, y: int, x: int, h: int, w: int):
    for i in range(h):
        stdscr.addstr(y + i, x, " " * w, curses.color_pair(1))
    
    stdscr.addstr(y, x, "═══ 日志 ═══".center(w), curses.color_pair(2) | curses.A_BOLD)
    
    recent_logs = game.log[-(h - 2):]
    for i, line in enumerate(recent_logs):
        display_line = line[:w - 2]
        try:
            stdscr.addstr(y + 1 + i, x + 1, display_line, curses.color_pair(1))
        except:
            pass
    
    for j in range(w):
        stdscr.addstr(y, x + j, "═")


def render(stdscr, game: Game):
    stdscr.clear()
    max_y, max_x = stdscr.getmaxyx()
    if max_y < 25 or max_x < 80:
        stdscr.addstr(0, 0, "终端窗口太小！请至少 80x25", curses.color_pair(4) | curses.A_BOLD)
        stdscr.refresh()
        return
    
    log_h = 8
    main_h = max_y - log_h - 1
    
    draw_player_panel(stdscr, game, 0, 0, main_h, LEFT_PANEL_WIDTH)
    
    center_x = LEFT_PANEL_WIDTH
    center_w = max_x - LEFT_PANEL_WIDTH
    
    if game.scene == GameScene.MAP:
        draw_map_center(stdscr, game, 0, center_x, main_h, center_w)
    elif game.scene == GameScene.BATTLE:
        draw_battle_center(stdscr, game, 0, center_x, main_h, center_w)
    elif game.scene == GameScene.CARD_REWARD:
        draw_card_reward_center(stdscr, game, 0, center_x, main_h, center_w)
    elif game.scene in (GameScene.REST, GameScene.TREASURE, GameScene.SHOP):
        draw_event_center(stdscr, game, 0, center_x, main_h, center_w)
    elif game.scene in (GameScene.GAME_OVER, GameScene.VICTORY):
        draw_end_screen(stdscr, game, 0, center_x, main_h, center_w)
    
    draw_log(stdscr, game, max_y - log_h - 1, 0, log_h, max_x)
    stdscr.refresh()


def init_colors():
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_WHITE, 234)
    curses.init_pair(2, curses.COLOR_CYAN, 234)
    curses.init_pair(3, curses.COLOR_GREEN, 234)
    curses.init_pair(4, curses.COLOR_YELLOW, 234)
    curses.init_pair(5, curses.COLOR_MAGENTA, 234)
    curses.init_pair(6, curses.COLOR_BLUE, 234)
    curses.init_pair(7, curses.COLOR_WHITE, 234)
