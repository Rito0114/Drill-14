"""실행: python main.py (어느 작업 폴더에서 실행해도 리소스를 찾는다)."""

from pico2d import close_canvas, open_canvas

import game_framework
import play_mode


def main():
    open_canvas(play_mode.WIDTH, play_mode.HEIGHT)
    try:
        game_framework.run(play_mode)
    finally:
        close_canvas()


if __name__ == '__main__':
    main()
