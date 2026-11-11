"""한 장의 스프라이트를 공유하는 새 10마리의 비행 화면."""

from pathlib import Path
import random

from pico2d import (
    SDL_KEYDOWN, SDL_QUIT, SDLK_ESCAPE, SDLK_SPACE, SDLK_r,
    clear_canvas, draw_rectangle, get_events, load_font, load_image, update_canvas,
)

import game_framework
from bird import ANIMATION_FPS, FRAME_COUNT, DRAW_WIDTH, Bird

WIDTH, HEIGHT = 1280, 800
BIRD_COUNT = 10
ASSET_DIR = Path(__file__).resolve().parent
birds = []
image = None
title_font = None
body_font = None
small_font = None
paused = False


def reset_flock(seed=None):
    global birds
    rng = random.Random(seed)
    left, right = 78 + DRAW_WIDTH / 2, WIDTH - 28 - DRAW_WIDTH / 2
    birds = [
        Bird(
            x=rng.uniform(left, right), y=120 + index * 56,
            speed=rng.uniform(140, 230), direction=1 if index % 2 == 0 else -1,
            left=left, right=right, phase=rng.uniform(0, FRAME_COUNT),
        )
        for index in range(BIRD_COUNT)
    ]


def init():
    global image, title_font, body_font, small_font, paused
    image = load_image(str(ASSET_DIR / 'bird_animation.png'))
    font_path = str(ASSET_DIR / 'ENCR10B.TTF')
    title_font = load_font(font_path, 30)
    body_font = load_font(font_path, 17)
    small_font = load_font(font_path, 13)
    paused = False
    reset_flock()


def handle_events():
    global paused
    for event in get_events():
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                game_framework.quit()
            elif event.key == SDLK_SPACE and not getattr(event, 'repeat', 0):
                paused = not paused
            elif event.key == SDLK_r and not getattr(event, 'repeat', 0):
                reset_flock()


def update():
    if not paused:
        for bird in birds:
            bird.update(game_framework.frame_time)


def render():
    clear_canvas()
    draw_rectangle(0, 0, WIDTH - 1, HEIGHT - 1, 244, 247, 251, filled=True)
    draw_rectangle(0, 690, WIDTH - 1, HEIGHT - 1, 24, 39, 61, filled=True)
    title_font.draw(30, 751, 'DRILL 14 / BIRDS IN FLIGHT', (255, 255, 255))
    body_font.draw(32, 711, '10 BIRDS   /   14 FRAMES   /   12 FPS WING CYCLE', (160, 210, 232))
    body_font.draw(1110, 748, 'PAUSED' if paused else 'FLYING', (255, 213, 112))

    for index, bird in enumerate(birds):
        y = bird.y
        if index % 2 == 0:
            draw_rectangle(20, y - 27, WIDTH - 21, y + 27, 234, 241, 248, filled=True)
        small_font.draw(32, y + 4, f'{index + 1:02}', (106, 124, 145))
        # 옅은 비행 경로를 먼저 그리고 모든 새를 그 위에 표시한다.
        for x in range(96, WIDTH - 32, 28):
            draw_rectangle(x, y - 1, x + 8, y, 210, 223, 235, filled=True)
    for bird in birds:
        bird.draw(image)

    draw_rectangle(0, 0, WIDTH - 1, 62, 255, 255, 255, filled=True)
    body_font.draw(30, 37, 'SPACE  PAUSE / RESUME     R  RESET FLOCK     ESC  EXIT', (49, 67, 90))
    small_font.draw(30, 14, f'DELTA-TIME MOTION   |   {ANIMATION_FPS:g} SPRITE FRAMES / SECOND   |   SHARED SPRITE SHEET', (115, 131, 151))
    update_canvas()


def finish():
    global image, title_font, body_font, small_font
    birds.clear()
    image = title_font = body_font = small_font = None
