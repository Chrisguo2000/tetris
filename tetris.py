import random
import tkinter as tk


CELL_SIZE = 38
BOARD_WIDTH = 10
BOARD_HEIGHT = 20
PREVIEW_SIZE = 4
BOARD_PIXEL_WIDTH = BOARD_WIDTH * CELL_SIZE
BOARD_PIXEL_HEIGHT = BOARD_HEIGHT * CELL_SIZE
PANEL_WIDTH = 280
WINDOW_WIDTH = BOARD_PIXEL_WIDTH + PANEL_WIDTH + 84
WINDOW_HEIGHT = BOARD_PIXEL_HEIGHT + 72
TICK_MS = 400


SHAPES = {
    "I": {"color": "#43d9d9", "cells": [(0, 1), (1, 1), (2, 1), (3, 1)]},
    "J": {"color": "#4d73ff", "cells": [(0, 0), (0, 1), (1, 1), (2, 1)]},
    "L": {"color": "#ff9b54", "cells": [(2, 0), (0, 1), (1, 1), (2, 1)]},
    "O": {"color": "#ffd166", "cells": [(1, 0), (2, 0), (1, 1), (2, 1)]},
    "S": {"color": "#2ecf8f", "cells": [(1, 0), (2, 0), (0, 1), (1, 1)]},
    "T": {"color": "#c77dff", "cells": [(1, 0), (0, 1), (1, 1), (2, 1)]},
    "Z": {"color": "#ff5d73", "cells": [(0, 0), (1, 0), (1, 1), (2, 1)]},
}


def clamp(value: int) -> int:
    return max(0, min(255, value))


def shift_color(color: str, amount: int) -> str:
    color = color.lstrip("#")
    red = clamp(int(color[0:2], 16) + amount)
    green = clamp(int(color[2:4], 16) + amount)
    blue = clamp(int(color[4:6], 16) + amount)
    return f"#{red:02x}{green:02x}{blue:02x}"


class TetrisGame:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("霓虹俄罗斯方块")
        self.root.resizable(False, False)
        self.root.configure(bg="#07111f")

        self.board = [[None for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
        self.score = 0
        self.lines = 0
        self.level = 1
        self.game_over = False
        self.after_id = None

        self.current_piece = None
        self.next_piece = self.new_piece()

        self.build_ui()
        self.bind_keys()
        self.spawn_piece()
        self.schedule_tick()
        self.draw()

    def build_ui(self) -> None:
        self.background = tk.Canvas(
            self.root,
            width=WINDOW_WIDTH,
            height=WINDOW_HEIGHT,
            bg="#07111f",
            highlightthickness=0,
        )
        self.background.pack()
        self.draw_background()

        board_left = 36
        board_top = 36
        board_right = board_left + BOARD_PIXEL_WIDTH
        board_bottom = board_top + BOARD_PIXEL_HEIGHT
        panel_left = board_right + 24
        panel_right = panel_left + PANEL_WIDTH

        self.background.create_rectangle(
            board_left - 8,
            board_top - 8,
            board_right + 8,
            board_bottom + 8,
            fill="#12243b",
            outline="",
        )
        self.background.create_rectangle(
            board_left,
            board_top,
            board_right,
            board_bottom,
            fill="#0c1a2b",
            outline="#51e5ff",
            width=2,
        )
        self.background.create_rectangle(
            panel_left,
            board_top,
            panel_right,
            board_bottom,
            fill="#0f1b2d",
            outline="#23415f",
            width=2,
        )

        self.canvas = tk.Canvas(
            self.background,
            width=BOARD_PIXEL_WIDTH,
            height=BOARD_PIXEL_HEIGHT,
            bg="#0c1a2b",
            highlightthickness=0,
        )
        self.canvas.place(x=board_left, y=board_top)

        self.panel_canvas = tk.Canvas(
            self.background,
            width=PANEL_WIDTH,
            height=BOARD_PIXEL_HEIGHT,
            bg="#0f1b2d",
            highlightthickness=0,
        )
        self.panel_canvas.place(x=panel_left, y=board_top)

        self.preview = tk.Canvas(
            self.panel_canvas,
            width=PREVIEW_SIZE * CELL_SIZE + 28,
            height=PREVIEW_SIZE * CELL_SIZE + 28,
            bg="#13263b",
            highlightthickness=0,
        )
        self.preview.place(x=47, y=210)

    def draw_background(self) -> None:
        steps = 20
        for i in range(steps):
            ratio = i / max(steps - 1, 1)
            color = shift_color("#07111f", int(ratio * 55))
            y1 = int(i * WINDOW_HEIGHT / steps)
            y2 = int((i + 1) * WINDOW_HEIGHT / steps)
            self.background.create_rectangle(0, y1, WINDOW_WIDTH, y2, fill=color, outline=color)

        for x in range(0, WINDOW_WIDTH, 70):
            self.background.create_line(x, 0, x + 90, WINDOW_HEIGHT, fill="#0d2238", width=1)
        for y in range(0, WINDOW_HEIGHT, 60):
            self.background.create_line(0, y, WINDOW_WIDTH, y + 40, fill="#102942", width=1)

        self.background.create_text(
            42,
            16,
            text="NEON TETRIS",
            anchor="w",
            fill="#9ee7ff",
            font=("Avenir Next", 18, "bold"),
        )

    def bind_keys(self) -> None:
        self.root.bind("<Left>", lambda _: self.move(-1, 0))
        self.root.bind("<Right>", lambda _: self.move(1, 0))
        self.root.bind("<Down>", lambda _: self.soft_drop())
        self.root.bind("<Up>", lambda _: self.rotate())
        self.root.bind("<space>", lambda _: self.hard_drop())
        self.root.bind("r", lambda _: self.restart())
        self.root.bind("R", lambda _: self.restart())

    def new_piece(self) -> dict:
        shape_name = random.choice(list(SHAPES))
        shape = SHAPES[shape_name]
        return {
            "name": shape_name,
            "color": shape["color"],
            "cells": list(shape["cells"]),
            "x": 3,
            "y": 0,
        }

    def spawn_piece(self) -> None:
        self.current_piece = self.next_piece
        self.current_piece["x"] = 3
        self.current_piece["y"] = 0
        self.next_piece = self.new_piece()
        if not self.is_valid_position(self.current_piece["cells"], self.current_piece["x"], self.current_piece["y"]):
            self.end_game()

    def is_valid_position(self, cells, offset_x: int, offset_y: int) -> bool:
        for x, y in cells:
            board_x = x + offset_x
            board_y = y + offset_y
            if board_x < 0 or board_x >= BOARD_WIDTH or board_y >= BOARD_HEIGHT:
                return False
            if board_y >= 0 and self.board[board_y][board_x] is not None:
                return False
        return True

    def move(self, dx: int, dy: int) -> bool:
        if self.game_over:
            return False
        new_x = self.current_piece["x"] + dx
        new_y = self.current_piece["y"] + dy
        if self.is_valid_position(self.current_piece["cells"], new_x, new_y):
            self.current_piece["x"] = new_x
            self.current_piece["y"] = new_y
            self.draw()
            return True
        return False

    def rotate(self) -> None:
        if self.game_over or self.current_piece["name"] == "O":
            return

        rotated = [(-y + 1, x) for x, y in self.current_piece["cells"]]
        min_x = min(x for x, _ in rotated)
        min_y = min(y for _, y in rotated)
        normalized = [(x - min_x, y - min_y) for x, y in rotated]

        kicks = [(0, 0), (-1, 0), (1, 0), (-2, 0), (0, -1)]
        for kick_x, kick_y in kicks:
            new_x = self.current_piece["x"] + kick_x
            new_y = self.current_piece["y"] + kick_y
            if self.is_valid_position(normalized, new_x, new_y):
                self.current_piece["cells"] = normalized
                self.current_piece["x"] = new_x
                self.current_piece["y"] = new_y
                self.draw()
                return

    def soft_drop(self) -> None:
        if self.game_over:
            return
        if self.move(0, 1):
            self.score += 1
            self.draw()
        else:
            self.lock_piece()

    def hard_drop(self) -> None:
        if self.game_over:
            return
        while self.move(0, 1):
            self.score += 2
        self.lock_piece()

    def lock_piece(self) -> None:
        for x, y in self.current_piece["cells"]:
            board_x = self.current_piece["x"] + x
            board_y = self.current_piece["y"] + y
            if 0 <= board_y < BOARD_HEIGHT:
                self.board[board_y][board_x] = self.current_piece["color"]

        cleared = self.clear_lines()
        if cleared:
            self.lines += cleared
            self.score += [0, 120, 320, 560, 900][cleared] * self.level
            self.level = self.lines // 10 + 1

        self.spawn_piece()
        self.draw()

    def clear_lines(self) -> int:
        new_board = [row for row in self.board if any(cell is None for cell in row)]
        cleared = BOARD_HEIGHT - len(new_board)
        while len(new_board) < BOARD_HEIGHT:
            new_board.insert(0, [None for _ in range(BOARD_WIDTH)])
        self.board = new_board
        return cleared

    def tick(self) -> None:
        if self.game_over:
            return
        if not self.move(0, 1):
            self.lock_piece()
        self.schedule_tick()

    def schedule_tick(self) -> None:
        delay = max(90, TICK_MS - (self.level - 1) * 28)
        self.after_id = self.root.after(delay, self.tick)

    def end_game(self) -> None:
        self.game_over = True
        self.draw()

    def restart(self) -> None:
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
        self.board = [[None for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
        self.score = 0
        self.lines = 0
        self.level = 1
        self.game_over = False
        self.current_piece = None
        self.next_piece = self.new_piece()
        self.spawn_piece()
        self.schedule_tick()
        self.draw()

    def get_ghost_y(self) -> int:
        ghost_y = self.current_piece["y"]
        while self.is_valid_position(self.current_piece["cells"], self.current_piece["x"], ghost_y + 1):
            ghost_y += 1
        return ghost_y

    def draw_block(self, canvas: tk.Canvas, x1: int, y1: int, color: str, ghost: bool = False) -> None:
        x2 = x1 + CELL_SIZE
        y2 = y1 + CELL_SIZE
        if ghost:
            canvas.create_rectangle(x1 + 3, y1 + 3, x2 - 3, y2 - 3, outline=shift_color(color, 70), width=2, dash=(4, 2))
            return

        shadow = shift_color(color, -70)
        highlight = shift_color(color, 65)
        inner = shift_color(color, -20)

        canvas.create_rectangle(x1 + 2, y1 + 4, x2 + 2, y2 + 4, fill=shadow, outline="")
        canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=highlight, width=2)
        canvas.create_rectangle(x1 + 4, y1 + 4, x2 - 4, y2 - 4, fill=inner, outline="")
        canvas.create_polygon(
            x1 + 3,
            y1 + 3,
            x1 + CELL_SIZE - 3,
            y1 + 3,
            x1 + CELL_SIZE - 11,
            y1 + 11,
            x1 + 11,
            y1 + 11,
            fill=highlight,
            outline="",
        )

    def draw_cell(self, canvas: tk.Canvas, x: int, y: int, color: str, ghost: bool = False) -> None:
        self.draw_block(canvas, x * CELL_SIZE, y * CELL_SIZE, color, ghost=ghost)

    def draw_board(self) -> None:
        self.canvas.delete("all")

        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                x1 = x * CELL_SIZE
                y1 = y * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE
                base = "#11243a" if (x + y) % 2 == 0 else "#0d1d31"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=base, outline="#16304b")

        ghost_y = self.get_ghost_y()
        if ghost_y != self.current_piece["y"]:
            for x, y in self.current_piece["cells"]:
                draw_x = self.current_piece["x"] + x
                draw_y = ghost_y + y
                if draw_y >= 0:
                    self.draw_cell(self.canvas, draw_x, draw_y, self.current_piece["color"], ghost=True)

        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                color = self.board[y][x]
                if color:
                    self.draw_cell(self.canvas, x, y, color)

        for x, y in self.current_piece["cells"]:
            draw_x = self.current_piece["x"] + x
            draw_y = self.current_piece["y"] + y
            if draw_y >= 0:
                self.draw_cell(self.canvas, draw_x, draw_y, self.current_piece["color"])

        self.canvas.create_rectangle(0, 0, BOARD_PIXEL_WIDTH, 18, fill="#5de2ff", outline="", stipple="gray25")

        if self.game_over:
            self.canvas.create_rectangle(20, 215, 280, 385, fill="#07111f", outline="#81ecff", width=2)
            self.canvas.create_text(
                150,
                255,
                text="GAME OVER",
                fill="#d6f6ff",
                font=("Avenir Next", 22, "bold"),
            )
            self.canvas.create_text(
                150,
                298,
                text="按 R 重新开始",
                fill="#9bc9d8",
                font=("Helvetica", 13),
            )
            self.canvas.create_text(
                150,
                338,
                text=f"最终分数 {self.score}",
                fill="#ffd166",
                font=("Helvetica", 15, "bold"),
            )

    def draw_preview(self) -> None:
        self.preview.delete("all")
        self.preview.create_rectangle(0, 0, PREVIEW_SIZE * CELL_SIZE + 28, PREVIEW_SIZE * CELL_SIZE + 28, fill="#13263b", outline="#2b557c", width=2)

        cells = self.next_piece["cells"]
        min_x = min(x for x, _ in cells)
        max_x = max(x for x, _ in cells)
        min_y = min(y for _, y in cells)
        max_y = max(y for _, y in cells)
        shape_width = (max_x - min_x + 1) * CELL_SIZE
        shape_height = (max_y - min_y + 1) * CELL_SIZE
        offset_x = ((PREVIEW_SIZE * CELL_SIZE + 28) - shape_width) // 2 - min_x * CELL_SIZE
        offset_y = ((PREVIEW_SIZE * CELL_SIZE + 28) - shape_height) // 2 - min_y * CELL_SIZE

        for x, y in cells:
            self.draw_block(
                self.preview,
                offset_x + x * CELL_SIZE,
                offset_y + y * CELL_SIZE,
                self.next_piece["color"],
            )

    def draw_panel(self) -> None:
        self.panel_canvas.delete("all")
        self.panel_canvas.create_text(
            22,
            24,
            text="霓虹俄罗斯方块",
            anchor="w",
            fill="#ecfeff",
            font=("Avenir Next", 19, "bold"),
        )
        self.panel_canvas.create_text(
            22,
            56,
            text="经典玩法，赛博风格",
            anchor="w",
            fill="#74c4da",
            font=("Helvetica", 11),
        )

        cards = [
            ("分数", str(self.score), "#7bdff2", 92),
            ("消行", str(self.lines), "#ffd166", 146),
            ("等级", str(self.level), "#90f1b8", 200),
        ]
        for title, value, accent, y in cards:
            self.panel_canvas.create_rectangle(22, y, 228, y + 42, fill="#13263b", outline="#224969", width=2)
            self.panel_canvas.create_rectangle(22, y, 28, y + 42, fill=accent, outline="")
            self.panel_canvas.create_text(42, y + 14, text=title, anchor="w", fill="#7fb4c7", font=("Helvetica", 11))
            self.panel_canvas.create_text(208, y + 21, text=value, anchor="e", fill="#f7fbff", font=("Avenir Next", 16, "bold"))

        self.panel_canvas.create_text(
            22,
            340,
            text="下一个方块",
            anchor="w",
            fill="#ecfeff",
            font=("Helvetica", 13, "bold"),
        )
        self.panel_canvas.create_rectangle(22, 370, 228, 525, fill="#13263b", outline="#224969", width=2)

        controls_text = (
            "操作指南\n"
            "← →  左右移动\n"
            "↑    旋转方块\n"
            "↓    加速下落\n"
            "空格  直接落下\n"
            "R    重新开始"
        )
        self.panel_canvas.create_text(
            22,
            548,
            text=controls_text,
            anchor="nw",
            justify="left",
            fill="#b8d8e4",
            font=("Menlo", 11),
        )

        if self.game_over:
            self.panel_canvas.create_text(
                22,
                520,
                text="这一局结束了，再来一把。",
                anchor="w",
                fill="#ff8b94",
                font=("Helvetica", 11, "bold"),
            )

    def draw(self) -> None:
        self.draw_board()
        self.draw_panel()
        self.draw_preview()


def main() -> None:
    root = tk.Tk()
    TetrisGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
