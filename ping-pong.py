import pyxel
from enum import Enum
from dataclasses import dataclass
from abc import abstractmethod
import digit


class GameState(Enum):
    INIT = -1
    TITLE = 10
    READY = 0
    PAUSE = 1
    PLAYING = 2
    GAME_OVER = 3

game_state: GameState = GameState.INIT
left_player_win: bool = False
right_player_win: bool = False

@dataclass
class GameConfig:
    width: int = 160
    height: int = 120
    title: str = "Pyxel Pong"
    fps: int = 30
    scale: int = 1
    base_col = 1
    line_col = 6

def clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(value, max_value))

def text_center(texts: list[str], col: int = 7) -> None:
    pivot_x = GameConfig.width // 2
    pivot_y = GameConfig.height // 2
    font_w = 4
    font_h = 8
    for i in range(len(texts)):
        text = texts[i]
        text_width = font_w * len(text)
        pyxel.rect(pivot_x - text_width // 2-1, pivot_y - font_h * (0.5 - i)-1, text_width+1, font_h+1, GameConfig.base_col)
        pyxel.text(pivot_x - text_width // 2, pivot_y - font_h * (0.5 - i), text, col)

@abstractmethod
@dataclass
class RectCollider:
    x: float
    y: float
    w: int
    h: int
    
    def is_colliding(self, other: 'RectCollider') -> bool:
        return (self.x < other.x + other.w and
                self.x + self.w > other.x and
                self.y < other.y + other.h and
                self.y + self.h > other.y)

class Pong(RectCollider):
    def __init__(self) -> None:
        size = 3
        super().__init__(
            x=GameConfig.width // 2 - size // 2, 
            y=GameConfig.height // 2 - size // 2, 
            w=size, 
            h=size)
        self.speed = 2
        self.dx = 0.0
        self.dy = 0.0
        self.is_active = True
    
        self.start_dash()
    
    def start_dash(self) -> None:
        self.dx = pyxel.rndf(0.3, 1) * (1 if pyxel.rndi(0, 1) == 0 else -1)
        self.dy = pyxel.rndf(-1, 1)
        norm = (self.dx**2 + self.dy**2) ** 0.5
        if norm == 0:
            self.dx = self.speed
            self.dy = self.speed
            norm = (self.dx**2 + self.dy**2) ** 0.5
        self.dx = self.speed * self.dx / norm
        self.dy = self.speed * self.dy / norm
    
    def update(self, colliders: list['RectCollider']) -> None:
        if not self.is_active:
            self.x = GameConfig.width // 2 - self.w // 2
            self.y = GameConfig.height // 2 - self.h // 2
            self.start_dash()
            self.is_active = True
        
        # Update logic for Psong can be added here
        if self.x < 0 or self.x > GameConfig.width - self.w - 1:
            self.is_active = False
        if self.y < 1 or self.y > GameConfig.height - self.h - 1:
            self.dy = -self.dy
            if self.y < 1:
                self.y = 1
            elif self.y > GameConfig.height - self.h - 1:
                self.y = GameConfig.height - self.h - 1
            
        for collider in colliders:
            if self.is_colliding(collider):
                if isinstance(collider, Cursor):
                    # Reflect the ball based on the cursor's position
                    self.dx = -self.dx
                    # Adjust the ball's vertical speed based on where it hit the cursor
                    hit_pos = (self.y + self.h / 2) - (collider.y + collider.h / 2)
                    self.dy = hit_pos / (collider.h / 2) * self.speed
                else:
                    # If colliding with something else, just reverse the direction
                    self.dx = -self.dx
            
        self.x += self.dx
        self.y += self.dy
    
    def draw(self) -> None:
        if not self.is_active:
            return
        pyxel.rect(self.x, self.y, self.w, self.h, GameConfig.line_col)


class Cursor(RectCollider):
    def __init__(self, arrow_input: bool = False) -> None:
        super().__init__(
            x=0,
            y=0, 
            w=2, 
            h=24)
        self.dy = 0
        self.ay = GameConfig.height / (GameConfig.fps * 8)
        self.max_dy = GameConfig.height / (GameConfig.fps * 2)
        
        self.up_input = pyxel.KEY_UP
        self.down_input = pyxel.KEY_DOWN
        if arrow_input is False:
            self.up_input = pyxel.KEY_W
            self.down_input = pyxel.KEY_S
    
    def set_default_pos(self, x: int = 0, y: int = 0) -> None:
        self.x = x
        self.y = y
        self.dy = 0
    
    def update(self) -> None:   
        if pyxel.btn(self.up_input):
            self.dy = clamp(self.dy - self.ay, -self.max_dy, self.max_dy)
        if pyxel.btn(self.down_input):
            self.dy = clamp(self.dy + self.ay, -self.max_dy, self.max_dy)
        if not pyxel.btn(self.up_input) and not pyxel.btn(self.down_input):
            self.dy -= pyxel.sgn(self.dy) * self.ay
        
        self.y += self.dy
        
        if self.y < 1:
            self.y = 1
            self.dy = 0
        if self.y > GameConfig.height - self.h - 1:
            self.y = GameConfig.height - self.h - 1
            self.dy = 0
            
    def draw(self) -> None:
        pyxel.rect(self.x, self.y, self.w, self.h, GameConfig.line_col)


class App:
    def __init__(self) -> None:
        c = GameConfig()
        global game_state
        game_state = GameState.INIT
        pyxel.init(c.width, c.height, title=c.title, fps=c.fps)
        self.cursor1 = Cursor(arrow_input=False)
        self.cursor2 = Cursor(arrow_input=True)
        self.pong = Pong()
        self.cursor1.set_default_pos(0+5, GameConfig.height//2-self.cursor1.h//2)
        self.cursor2.set_default_pos(GameConfig.width-5, GameConfig.height//2-self.cursor2.h//2)
        
        self.right_player_score = 0
        self.left_player_score = 0
        
        self.pong.is_active = False
        game_state = GameState.TITLE
        
        self.timer = -1
        pyxel.run(self.update, self.draw)
        
    def update(self) -> None:
        global game_state

        if game_state == GameState.TITLE:
            if pyxel.btnp(pyxel.KEY_SPACE):
                game_state = GameState.READY
            self.cursor1.update()
            self.cursor2.update()
            return
        if game_state == GameState.READY:
            if self.timer == -1:
                self.timer = GameConfig.fps * 2
            self.timer -= 1
            if self.timer <= 0:
                game_state = GameState.PLAYING
                self.timer = -1

            self.cursor1.update()
            self.cursor2.update()
                
        elif game_state == GameState.PAUSE:
            if pyxel.btnp(pyxel.KEY_SPACE):
                game_state = GameState.PLAYING
            else:
                return
            
        elif game_state == GameState.GAME_OVER:
            if pyxel.btnp(pyxel.KEY_SPACE):
                game_state = GameState.READY
                self.left_player_score = 0
                self.right_player_score = 0
                self.cursor1.set_default_pos(0+5, GameConfig.height//2-15)
                self.cursor2.set_default_pos(GameConfig.width-5, GameConfig.height//2-15)
                return
        
        elif game_state == GameState.PLAYING:
            if pyxel.btnp(pyxel.KEY_SPACE):
                game_state = GameState.PAUSE
                return
            
            self.cursor1.update()
            self.cursor2.update()
            self.pong.update([self.cursor1, self.cursor2])
        
            if self.pong.is_active is False:
                if self.pong.x < 0:
                    self.right_player_score += 1
                    game_state = GameState.READY
                elif self.pong.x > GameConfig.width - self.pong.w - 1:
                    self.left_player_score += 1
                    game_state = GameState.READY
                    
                if self.left_player_score >= 10 or self.right_player_score >= 10:
                    global left_player_win
                    global right_player_win
                    if self.left_player_score - self.right_player_score >= 2:
                        left_player_win = True
                        right_player_win = False
                        game_state = GameState.GAME_OVER
                        self.pong.is_active = False
                    elif self.right_player_score - self.left_player_score >= 2:
                        left_player_win = False
                        right_player_win = True
                        game_state = GameState.GAME_OVER
                        self.pong.is_active = False

    
    def draw(self) -> None:
        pyxel.cls(GameConfig.base_col)
        
        pyxel.line(0, 0, GameConfig.width, 0, GameConfig.line_col)
        pyxel.line(0, GameConfig.height-1, GameConfig.width, GameConfig.height-1, GameConfig.line_col)
        for i in range(0, GameConfig.height, 8):
            pyxel.line(GameConfig.width // 2, i, GameConfig.width // 2, i + 4, GameConfig.line_col)
        
        global game_state
        if game_state == GameState.TITLE:
            text_center(["Pyxel Pong", "Press SPACE to start"], GameConfig.line_col)
        if game_state == GameState.READY:
            text_center(["Ready..."], GameConfig.line_col)
        elif game_state == GameState.PAUSE:
            text_center(["Press SPACE to resume"], GameConfig.line_col)
        elif game_state == game_state.PLAYING:
            text_center(["Game"], GameConfig.line_col)
        elif game_state == GameState.GAME_OVER:
            text_center(
                ["Game Over", "Press SPACE to restart"],
                GameConfig.line_col)
            if left_player_win:
                pyxel.text(GameConfig.width // 2 - 32, GameConfig.height // 4, "Win", GameConfig.line_col)
                pyxel.text(GameConfig.width // 2 + 20, GameConfig.height // 4, "Lose", GameConfig.line_col)
            elif right_player_win:
                pyxel.text(GameConfig.width // 2 - 32, GameConfig.height // 4, "Lose", GameConfig.line_col)
                pyxel.text(GameConfig.width // 2 + 20, GameConfig.height // 4, "Win", GameConfig.line_col)
        
        self.cursor1.draw()
        self.cursor2.draw()
        self.pong.draw()
        
        digit.draw(digit.DigitPivot.TOP_LEFT, GameConfig.width // 2 -8, 5, self.left_player_score, GameConfig.line_col)
        digit.draw(digit.DigitPivot.TOP_RIGHT, GameConfig.width // 2 + 8, 5, self.right_player_score, GameConfig.line_col)

App()