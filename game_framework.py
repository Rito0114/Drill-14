"""LEC16의 모드 스택에 현재 프레임 경과 시간과 종료 정리를 적용한다."""

import time

frame_time = 0.0
running = False
stack = []
TARGET_FPS = 60


def change_mode(mode):
    if stack:
        stack.pop().finish()
    stack.append(mode)
    mode.init()


def push_mode(mode):
    if stack:
        stack[-1].pause()
    stack.append(mode)
    mode.init()


def pop_mode():
    if stack:
        stack.pop().finish()
    if stack:
        stack[-1].resume()
    else:
        quit()


def quit():
    global running
    running = False


def run(start_mode):
    global frame_time, running, stack
    running = True
    frame_time = 0.0
    stack = [start_mode]
    try:
        start_mode.init()
        previous_time = time.perf_counter()
        while running:
            frame_start = time.perf_counter()
            frame_time = frame_start - previous_time
            previous_time = frame_start
            stack[-1].handle_events()
            if not running:
                break
            stack[-1].update()
            stack[-1].render()
            # CPU 점유만 줄인다. 실제 속도는 FPS가 아니라 frame_time으로 결정한다.
            remaining = 1.0 / TARGET_FPS - (time.perf_counter() - frame_start)
            if remaining > 0:
                time.sleep(remaining)
    finally:
        try:
            while stack:
                stack.pop().finish()
        finally:
            running = False
            frame_time = 0.0
