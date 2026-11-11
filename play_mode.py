"""LEC16의 소년·잔디·공 플레이 화면에 새 10마리를 추가한다."""

from pathlib import Path
import random

from pico2d import (
    SDL_KEYDOWN, SDL_QUIT, SDLK_ESCAPE, SDLK_p, SDLK_r,
    clear_canvas, draw_rectangle, get_events, load_font, load_image, update_canvas,
)

import game_framework
import game_world
from ball import Ball
from bird import FRAME_COUNT, DRAW_WIDTH, Bird
from boy import Boy
from grass import Grass
from flock import Flock

WIDTH, HEIGHT = 1600, 600
BIRD_COUNT = 10
ASSET_DIR = Path(__file__).resolve().parent
birds = []
flock = None
boy = None
grass = None
image = None
body_font = None
paused = False


def reset_flock(seed=None):
    global birds, flock
    if flock is not None:
        game_world.remove_object(flock)
    rng = random.Random(seed)
    left, right = DRAW_WIDTH / 2 + 10, WIDTH - DRAW_WIDTH / 2 - 10
    # 일부 새는 높이를 공유한다. 개별 행이나 구획으로 나누지 않는다.
    heights = [300, 380, 460, 380, 300, 220, 300, 380, 460, 380]
    if rng.random() < 0.5:
        heights.reverse()
    center = WIDTH / 2 + rng.uniform(-60, 60)
    birds = [
        Bird(
            x=center + (index - 4.5) * 70,
            y=heights[index], speed=200.0, direction=1,
            left=left, right=right, phase=rng.uniform(0, FRAME_COUNT), image=image,
        )
        for index in range(BIRD_COUNT)
    ]
    flock = Flock(birds, WIDTH)
    game_world.add_oject(flock, 1)


def init():
    global image, body_font, boy, grass, paused
    game_world.clear()
    image = load_image(str(ASSET_DIR / 'bird_animation.png'))
    body_font = load_font(str(ASSET_DIR / 'ENCR10B.TTF'), 17)
    boy = Boy()
    grass = Grass()
    game_world.add_oject(grass, 0)
    game_world.add_oject(boy, 1)
    paused = False
    reset_flock()


def handle_events():
    global paused
    for event in get_events():
        if event.type == SDL_QUIT:
            game_framework.quit()
            return
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
            return
        elif event.type == SDL_KEYDOWN and event.key == SDLK_p:
            if not getattr(event, 'repeat', 0):
                paused = not paused
                boy.pause()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_r:
            if not getattr(event, 'repeat', 0):
                reset_flock()
        elif not paused:
            boy.handle_event(event)


def pause():
    boy.pause()


def resume():
    pass


def update():
    if not paused:
        game_world.update()


def render():
    clear_canvas()
    game_world.render()
    draw_rectangle(0, HEIGHT - 39, WIDTH - 1, HEIGHT - 1, 24, 39, 61, filled=True)
    body_font.draw(16, HEIGHT - 23, 'DRILL 14 | LEC16 + 10 BIRDS | 14 FRAMES', (255, 255, 255))
    body_font.draw(670, HEIGHT - 23, 'ARROWS MOVE | SPACE FIRE / WAKE | P PAUSE | R BIRDS | ESC EXIT', (190, 220, 240))
    if paused:
        body_font.draw(WIDTH - 95, HEIGHT - 65, 'PAUSED', (140, 40, 25))
    update_canvas()


def finish():
    global image, body_font, boy, grass, flock
    game_world.clear()
    birds.clear()
    image = body_font = boy = grass = None
    flock = None
    Ball.images.clear()
