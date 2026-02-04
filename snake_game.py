#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
贪吃蛇游戏
使用方向键控制，Q键退出
"""

import curses
import random
import time

class SnakeGame:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.setup_screen()
        self.reset_game()
        
    def setup_screen(self):
        """初始化屏幕设置"""
        curses.curs_set(0)  # 隐藏光标
        self.stdscr.nodelay(1)  # 非阻塞输入
        self.stdscr.timeout(100)  # 刷新间隔（毫秒）
        
        # 获取屏幕尺寸
        self.height, self.width = self.stdscr.getmaxyx()
        
        # 游戏区域（留边距）
        self.game_height = self.height - 2
        self.game_width = self.width - 2
        
    def reset_game(self):
        """重置游戏状态"""
        # 蛇的初始位置（屏幕中央）
        self.snake = [
            [self.game_height // 2, self.game_width // 2],
            [self.game_height // 2, self.game_width // 2 - 1],
            [self.game_height // 2, self.game_width // 2 - 2]
        ]
        
        # 初始方向：向右
        self.direction = curses.KEY_RIGHT
        
        # 分数
        self.score = 0
        
        # 生成第一个食物
        self.food = self.generate_food()
        
        # 游戏状态
        self.game_over = False
        
    def generate_food(self):
        """生成食物位置"""
        while True:
            food = [
                random.randint(1, self.game_height - 1),
                random.randint(1, self.game_width - 1)
            ]
            if food not in self.snake:
                return food
                
    def draw_border(self):
        """绘制边界"""
        for y in range(self.game_height + 1):
            self.stdscr.addch(y, 0, '│')
            self.stdscr.addch(y, self.game_width + 1, '│')
        for x in range(self.game_width + 2):
            self.stdscr.addch(0, x, '─')
            self.stdscr.addch(self.game_height + 1, x, '─')
        # 角落
        self.stdscr.addch(0, 0, '┌')
        self.stdscr.addch(0, self.game_width + 1, '┐')
        self.stdscr.addch(self.game_height + 1, 0, '└')
        self.stdscr.addch(self.game_height + 1, self.game_width + 1, '┘')
        
    def draw_snake(self):
        """绘制蛇"""
        for i, segment in enumerate(self.snake):
            char = '█' if i == 0 else '▓'  # 蛇头用实心，身体用半实心
            try:
                self.stdscr.addch(segment[0], segment[1], char)
            except curses.error:
                pass
                
    def draw_food(self):
        """绘制食物"""
        try:
            self.stdscr.addch(self.food[0], self.food[1], '●')
        except curses.error:
            pass
            
    def draw_score(self):
        """显示分数"""
        score_text = f" 分数: {self.score} "
        try:
            self.stdscr.addstr(0, self.width // 2 - len(score_text) // 2, score_text)
        except curses.error:
            pass
            
    def draw_game_over(self):
        """显示游戏结束"""
        messages = [
            "游戏结束!",
            f"最终分数: {self.score}",
            "按 R 重新开始",
            "按 Q 退出"
        ]
        
        start_y = self.height // 2 - len(messages) // 2
        for i, msg in enumerate(messages):
            start_x = self.width // 2 - len(msg) // 2
            try:
                self.stdscr.addstr(start_y + i, start_x, msg)
            except curses.error:
                pass
                
    def handle_input(self):
        """处理键盘输入"""
        key = self.stdscr.getch()
        
        if key == ord('q') or key == ord('Q'):
            return 'quit'
        elif key == ord('r') or key == ord('R'):
            if self.game_over:
                self.reset_game()
                return 'restart'
                
        # 防止反向移动
        if key in [curses.KEY_UP, ord('w'), ord('W')] and self.direction != curses.KEY_DOWN:
            self.direction = curses.KEY_UP
        elif key in [curses.KEY_DOWN, ord('s'), ord('S')] and self.direction != curses.KEY_UP:
            self.direction = curses.KEY_DOWN
        elif key in [curses.KEY_LEFT, ord('a'), ord('A')] and self.direction != curses.KEY_RIGHT:
            self.direction = curses.KEY_LEFT
        elif key in [curses.KEY_RIGHT, ord('d'), ord('D')] and self.direction != curses.KEY_LEFT:
            self.direction = curses.KEY_RIGHT
            
        return None
        
    def move_snake(self):
        """移动蛇"""
        # 计算新头部位置
        head = self.snake[0].copy()
        
        if self.direction == curses.KEY_UP:
            head[0] -= 1
        elif self.direction == curses.KEY_DOWN:
            head[0] += 1
        elif self.direction == curses.KEY_LEFT:
            head[1] -= 1
        elif self.direction == curses.KEY_RIGHT:
            head[1] += 1
            
        # 检查碰撞
        if (head[0] <= 0 or head[0] >= self.game_height + 1 or
            head[1] <= 0 or head[1] >= self.game_width + 1 or
            head in self.snake):
            self.game_over = True
            return
            
        # 移动蛇
        self.snake.insert(0, head)
        
        # 检查是否吃到食物
        if head == self.food:
            self.score += 10
            self.food = self.generate_food()
            # 加快游戏速度
            if self.score % 50 == 0:
                current_timeout = self.stdscr.timeout()
                self.stdscr.timeout(max(50, current_timeout - 10))
        else:
            # 没吃到食物，删除尾部
            self.snake.pop()
            
    def draw(self):
        """绘制游戏画面"""
        self.stdscr.clear()
        self.draw_border()
        self.draw_snake()
        self.draw_food()
        self.draw_score()
        
        if self.game_over:
            self.draw_game_over()
            
        self.stdscr.refresh()
        
    def run(self):
        """游戏主循环"""
        while True:
            result = self.handle_input()
            
            if result == 'quit':
                break
                
            if not self.game_over:
                self.move_snake()
                
            self.draw()
            time.sleep(0.05)


def main():
    """主函数"""
    try:
        curses.wrapper(lambda stdscr: SnakeGame(stdscr).run())
    except KeyboardInterrupt:
        print("\n游戏已退出")
    except Exception as e:
        print(f"错误: {e}")
        print("提示: 请确保终端支持 curses")


if __name__ == "__main__":
    main()
