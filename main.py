import curses
import sys
from game.game import Game, GameScene
from game.ui import render, init_colors


def main(stdscr):
    curses.curs_set(0)
    stdscr.keypad(True)
    init_colors()
    
    game = Game()
    
    while True:
        render(stdscr, game)
        
        try:
            key = stdscr.getch()
        except KeyboardInterrupt:
            break
        
        if key == ord('q') or key == ord('Q'):
            if game.scene in (GameScene.GAME_OVER, GameScene.VICTORY):
                break
            if game.scene == GameScene.SHOP:
                game.leave_shop()
                continue
            break
        
        if game.scene in (GameScene.GAME_OVER, GameScene.VICTORY):
            if key == 10 or key == 13:
                game = Game()
            continue
        
        if game.scene == GameScene.MAP:
            if key in (curses.KEY_UP, ord('w'), ord('W'), ord('a'), ord('A')):
                game.move_map_selection("left")
            elif key in (curses.KEY_DOWN, ord('s'), ord('S'), ord('d'), ord('D')):
                game.move_map_selection("right")
            elif key in (10, 13):
                game.confirm_map_selection()
        
        elif game.scene == GameScene.BATTLE:
            if game.battle and game.battle.state.value == "player_turn":
                if ord('1') <= key <= ord('5'):
                    idx = key - ord('1')
                    game.battle_play_card(idx)
                elif key == ord(' '):
                    game.battle_end_turn()
        
        elif game.scene == GameScene.CARD_REWARD:
            if ord('1') <= key <= ord('3'):
                idx = key - ord('1')
                game.choose_card_reward(idx)
            elif key == ord('s') or key == ord('S'):
                game.skip_card_reward()
        
        elif game.scene == GameScene.REST:
            if key == ord('1'):
                game.choose_rest(0)
            elif key == ord('2'):
                game.choose_rest(1)
        
        elif game.scene == GameScene.TREASURE:
            if key in (10, 13):
                if game.treasure_event and game.treasure_event.claimed:
                    game._return_to_map()
                else:
                    game.claim_treasure()
        
        elif game.scene == GameScene.SHOP:
            if ord('1') <= key <= ord('5'):
                idx = key - ord('1')
                game.shop_buy_card(idx)
            elif key == ord('h') or key == ord('H'):
                game.shop_buy_heal()


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except Exception as e:
        print(f"游戏运行出错: {e}")
        print("请确保终端支持 256 色且窗口大小至少为 80x25")
        import traceback
        traceback.print_exc()
        sys.exit(1)
