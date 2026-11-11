"""현재 프레임의 경과 시간을 전달하는 단일 모드 게임 루프."""

import time

frame_time = 0.0
running = False
TARGET_FPS = 60


def quit():
    global running
    running = False


def run(start_mode):
    global frame_time, running
    running = True
    frame_time = 0.0
    try:
        start_mode.init()
        previous_time = time.perf_counter()
        while running:
            frame_start = time.perf_counter()
            frame_time = frame_start - previous_time
            previous_time = frame_start
            start_mode.handle_events()
            if not running:
                break
            start_mode.update()
            start_mode.render()
            # CPU 점유만 줄인다. 실제 속도는 FPS가 아니라 frame_time으로 결정한다.
            remaining = 1.0 / TARGET_FPS - (time.perf_counter() - frame_start)
            if remaining > 0:
                time.sleep(remaining)
    finally:
        try:
            start_mode.finish()
        finally:
            running = False
            frame_time = 0.0
