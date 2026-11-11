"""시간 기반 비행 모델. 이미지 로딩 없이도 운동과 프레임을 검증할 수 있다."""

from dataclasses import dataclass

FRAME_COUNT = 14
ANIMATION_FPS = 12.0
SHEET_COLUMNS = 5
SHEET_COLUMN_WIDTH = 182
SHEET_ROW_HEIGHT = 170
DRAW_WIDTH = 92
DRAW_HEIGHT = 84


def frame_rectangle(frame, image_width, image_height):
    """위→아래 행 순서를 pico2d의 왼쪽 아래 원점으로 변환한다."""
    if not 0 <= frame < FRAME_COUNT:
        raise ValueError('유효한 새 프레임은 0~13입니다.')
    row, column = divmod(frame, SHEET_COLUMNS)
    # 새의 기준 위치는 182픽셀 간격이다. 원본 우측 8픽셀은 여백이다.
    left = column * SHEET_COLUMN_WIDTH
    right = min((column + 1) * SHEET_COLUMN_WIDTH, image_width)
    # 둘째 행의 꼬리가 y=339까지 이어진다. 3등분하면 이웃 행이 섞인다.
    top = row * SHEET_ROW_HEIGHT
    bottom = min((row + 1) * SHEET_ROW_HEIGHT, image_height)
    return left, image_height - bottom, right - left, bottom - top


@dataclass
class Bird:
    x: float
    y: float
    speed: float
    direction: int
    left: float
    right: float
    phase: float = 0.0
    image: object = None

    def __post_init__(self):
        if self.right <= self.left or self.speed < 0:
            raise ValueError('이동 구간과 속도를 확인하세요.')
        if self.direction not in (-1, 1) or not self.left <= self.x <= self.right:
            raise ValueError('시작 위치와 비행 방향을 확인하세요.')
        self.phase %= FRAME_COUNT
        span = self.right - self.left
        offset = self.x - self.left
        self.travel = offset if self.direction == 1 else 2 * span - offset

    @property
    def frame(self):
        return int(self.phase) % FRAME_COUNT

    def advance_animation(self, dt):
        self.phase = (self.phase + ANIMATION_FPS * dt) % FRAME_COUNT
        # 부동소수점 누적으로 0프레임이 13.999999…로 남지 않게 한다.
        nearest = round(self.phase)
        if abs(self.phase - nearest) < 1e-10:
            self.phase = float(nearest % FRAME_COUNT)

    def update(self, dt=None):
        if dt is None:
            import game_framework
            dt = game_framework.frame_time
        if dt < 0:
            raise ValueError('경과 시간은 음수가 될 수 없습니다.')
        # 왕복 경로를 펼쳐 누적한 뒤 반으로 접는다. 초과 이동 거리를 보존한다.
        span = self.right - self.left
        self.travel = (self.travel + self.speed * dt) % (2 * span)
        if self.travel < span:
            self.x = self.left + self.travel
            self.direction = 1
        else:
            self.x = self.right - (self.travel - span)
            self.direction = -1
        self.advance_animation(dt)

    def draw(self, image=None):
        image = self.image if image is None else image
        source = frame_rectangle(self.frame, image.w, image.h)
        image.clip_composite_draw(
            *source, 0, 'h' if self.direction == -1 else '',
            self.x, self.y, DRAW_WIDTH, DRAW_HEIGHT,
        )
