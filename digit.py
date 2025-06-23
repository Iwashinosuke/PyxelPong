import pyxel
from enum import Enum

__digit_w = 8
__digit_h = 16
__line_th = 2
__digit_spacing = 2

class DigitPivot(Enum):
    TOP_LEFT = 0
    TOP_RIGHT = 1

def draw(pivot: DigitPivot, x: int, y: int, digit: int, col: int) -> None:
    if digit < 0 or digit > 99:
        return
    
    if pivot == DigitPivot.TOP_LEFT:
        x -= (__digit_w) * len(str(digit))
        
    for i, d in enumerate(str(digit)):
        __draw_digit(x + i * (__digit_w + __digit_spacing), y, d, col)

# [A, B, C, D, E, F, G]
# A: 上横, B: 右上縦, C: 右下縦, D: 下横, E: 左下縦, F: 左上縦, G: 中横    
SEGMENTS = {
    '0': [1,1,1,1,1,1,0],
    '1': [0,1,1,0,0,0,0],
    '2': [1,1,0,1,1,0,1],
    '3': [1,1,1,1,0,0,1],
    '4': [0,1,1,0,0,1,1],
    '5': [1,0,1,1,0,1,1],
    '6': [1,0,1,1,1,1,1],
    '7': [1,1,1,0,0,0,0],
    '8': [1,1,1,1,1,1,1],
    '9': [1,1,1,1,0,1,1],
}

def __draw_digit(x: int, y: int, ch: str, col: int) -> None:
    seg = SEGMENTS.get(ch)
    if not seg:
        return

    w, h, t = __digit_w, __digit_h, __line_th
    mid_y = y + h // 2 - t // 2

    # [A, B, C, D, E, F, G]
    # A: 上横, B: 右上縦, C: 右下縦, D: 下横, E: 左下縦, F: 左上縦, G: 中横
    if seg[0]:  pyxel.rect(x,         y,   w,      t,   col)  # A
    if seg[1]:  pyxel.rect(x + w-t,   y, t,      h//2, col)  # B
    if seg[2]:  pyxel.rect(x + w-t,   mid_y, t,      (h+t)//2, col)  # C
    if seg[3]:  pyxel.rect(x,         y + h-t, w,      t,   col)  # D
    if seg[4]:  pyxel.rect(x,         mid_y, t,      (h+t)//2, col)  # E
    if seg[5]:  pyxel.rect(x,         y,   t,      h//2, col)  # F
    if seg[6]:  pyxel.rect(x,         mid_y, w,      t,   col)  # G
    