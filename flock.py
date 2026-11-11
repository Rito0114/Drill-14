"""새떼 전체가 한 방향으로 이동하고 동시에 반사되는 공통 비행 모델."""

from bird import DRAW_WIDTH, Bird


class Flock:
    def __init__(self, birds, width, speed=200.0, direction=1):
        if len(birds) != 10:
            raise ValueError('새떼는 정확히 10마리로 구성합니다.')
        self.birds = birds
        center = (min(bird.x for bird in birds) + max(bird.x for bird in birds)) / 2
        self.offsets = [bird.x - center for bird in birds]
        # 양 끝 새의 스프라이트까지 화면 안에 남는 중심 이동 구간을 구한다.
        padding = DRAW_WIDTH / 2 + 10
        left = padding - min(self.offsets)
        right = width - padding - max(self.offsets)
        self.anchor = Bird(center, 0, speed, direction, left, right)
        for bird in birds:
            bird.speed = speed
            bird.direction = direction

    def update(self, dt=None):
        if dt is None:
            import game_framework
            dt = game_framework.frame_time
        self.anchor.update(dt)
        for bird, offset in zip(self.birds, self.offsets):
            bird.x = self.anchor.x + offset
            bird.direction = self.anchor.direction
            bird.advance_animation(dt)

    def draw(self):
        for bird in self.birds:
            bird.draw()
