from pico2d import *
from pathlib import Path

ASSET_DIR = Path(__file__).resolve().parent

class Grass:
    def __init__(self):
        self.image = load_image(str(ASSET_DIR / 'grass.png'))
        self.ruler_image = load_image(str(ASSET_DIR / 'ruler.png'))

    def update(self):
        pass

    def draw(self):
        self.image.draw(400, 30)
        self.image.draw(1200, 30)
        self.ruler_image.draw(800, 350)


