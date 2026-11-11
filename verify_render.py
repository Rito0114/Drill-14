"""실제 SDL 창에서 이벤트와 렌더링을 검증하고 스크린샷을 저장한다."""

import ctypes
from pathlib import Path
import struct
import zlib

import pico2d.pico2d as canvas
from sdl2 import (
    SDL_Event, SDL_KEYDOWN, SDL_PushEvent, SDL_RenderReadPixels,
    SDL_PIXELFORMAT_RGBA32, SDLK_ESCAPE, SDLK_SPACE, SDLK_r,
)

import game_framework
import main
import play_mode
from bird import DRAW_WIDTH, DRAW_HEIGHT


def save_screenshot(path):
    width, height = play_mode.WIDTH, play_mode.HEIGHT
    pixels = ctypes.create_string_buffer(width * height * 4)
    result = SDL_RenderReadPixels(canvas.renderer, None, SDL_PIXELFORMAT_RGBA32,
                                  pixels, width * 4)
    if result != 0:
        raise RuntimeError('SDL 화면 캡처 실패')

    def chunk(kind, content):
        return (struct.pack('>I', len(content)) + kind + content
                + struct.pack('>I', zlib.crc32(kind + content) & 0xffffffff))

    rows = b''.join(b'\0' + pixels.raw[y * width * 4:(y + 1) * width * 4]
                    for y in range(height))
    path.parent.mkdir(exist_ok=True)
    path.write_bytes(
        b'\x89PNG\r\n\x1a\n'
        + chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0))
        + chunk(b'IDAT', zlib.compress(rows)) + chunk(b'IEND', b'')
    )


def push_key(key):
    event = SDL_Event()
    event.type = SDL_KEYDOWN
    event.key.keysym.sym = key
    event.key.repeat = 0
    if SDL_PushEvent(ctypes.byref(event)) != 1:
        raise RuntimeError('SDL 키 이벤트 삽입 실패')


def verify():
    original_events = play_mode.handle_events
    original_present = play_mode.update_canvas
    original_init = play_mode.init
    original_finish = play_mode.finish
    state = dict(frame=0, paused_positions=None, resumed=False, reset=False,
                 finished=False, elapsed=0.0)
    output = Path(__file__).resolve().parent / 'screenshots'

    def init():
        original_init()
        play_mode.reset_flock(seed=14)
        assert len(play_mode.birds) == 10
        assert (play_mode.image.w, play_mode.image.h) == (918, 506)

    def events():
        frame = state['frame']
        state['frame'] += 1
        assert game_framework.frame_time >= 0
        state['elapsed'] += game_framework.frame_time
        before = [(bird.x, bird.phase) for bird in play_mode.birds]
        if frame in (20, 35):
            push_key(SDLK_SPACE)
        elif frame == 60:
            previous = list(play_mode.birds)
            push_key(SDLK_r)
        elif frame == 90:
            push_key(SDLK_ESCAPE)
        original_events()
        if frame == 20:
            assert play_mode.paused
            state['paused_positions'] = before
        elif 20 < frame <= 35:
            assert before == state['paused_positions'], '정지 중 위치/프레임 변경'
        if frame == 35:
            assert not play_mode.paused
        elif frame == 37:
            assert before != state['paused_positions'], '재개 후 이동하지 않음'
            state['resumed'] = True
        elif frame == 60:
            assert len(play_mode.birds) == 10
            assert all(new is not old for new, old in zip(play_mode.birds, previous))
            state['reset'] = True

    def present():
        for bird in play_mode.birds:
            assert 0 <= bird.frame < 14
            assert bird.x - DRAW_WIDTH / 2 >= 0
            assert bird.x + DRAW_WIDTH / 2 <= play_mode.WIDTH
            assert bird.y - DRAW_HEIGHT / 2 >= 0
            assert bird.y + DRAW_HEIGHT / 2 <= play_mode.HEIGHT
        if state['frame'] == 10:
            save_screenshot(output / 'flight.png')
        elif state['frame'] == 26:
            save_screenshot(output / 'paused.png')
        original_present()

    def finish():
        original_finish()
        state['finished'] = True

    play_mode.init = init
    play_mode.handle_events = events
    play_mode.update_canvas = present
    play_mode.finish = finish
    try:
        main.main()
    finally:
        play_mode.init = original_init
        play_mode.handle_events = original_events
        play_mode.update_canvas = original_present
        play_mode.finish = original_finish
    assert state['resumed'] and state['reset'] and state['finished']
    assert state['frame'] == 91 and state['elapsed'] > 0
    assert not game_framework.running and not play_mode.birds
    assert play_mode.image is None
    print('PASS: 10 birds, real SDL rendering, SPACE pause/resume, R reset, ESC exit, cleanup')
    print('Screenshots:', output)


if __name__ == '__main__':
    verify()
