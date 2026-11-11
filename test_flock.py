"""새떼 동시 이동·방향 전환 및 열 마리 전체의 가시성 검증."""

import unittest

from bird import DRAW_WIDTH, Bird
from flock import Flock


def make_flock():
    birds = [Bird(800 + (index - 4.5) * 70, 220 + index % 4 * 80,
                  200, 1, 56, 1544, phase=index) for index in range(10)]
    return Flock(birds, 1600)


class FlockTests(unittest.TestCase):
    def assert_visible_and_together(self, flock):
        self.assertEqual(len(flock.birds), 10)
        self.assertEqual(len({bird.direction for bird in flock.birds}), 1)
        self.assertEqual(len({bird.speed for bird in flock.birds}), 1)
        for bird, offset in zip(flock.birds, flock.offsets):
            self.assertGreaterEqual(bird.x - DRAW_WIDTH / 2, 0)
            self.assertLessEqual(bird.x + DRAW_WIDTH / 2, 1600)
            self.assertAlmostEqual(bird.x - flock.anchor.x, offset)

    def test_all_ten_stay_visible_and_hold_formation_for_30_seconds(self):
        for fps in (30, 60, 144):
            flock = make_flock()
            directions = set()
            for _ in range(fps * 30):
                flock.update(1 / fps)
                self.assert_visible_and_together(flock)
                directions.add(flock.birds[0].direction)
            self.assertEqual(directions, {-1, 1})

    def test_every_bird_turns_at_the_same_boundary(self):
        flock = make_flock()
        flock.update((flock.anchor.right - flock.anchor.x) / 200 + 0.1)
        self.assertEqual({bird.direction for bird in flock.birds}, {-1})
        self.assert_visible_and_together(flock)
        flock.update((flock.anchor.x - flock.anchor.left) / 200 + 0.1)
        self.assertEqual({bird.direction for bird in flock.birds}, {1})
        self.assert_visible_and_together(flock)
        flock.update(1000.25)
        self.assert_visible_and_together(flock)

    def test_flock_motion_independent_of_fps(self):
        expected = make_flock()
        expected.update(10)
        for fps in (30, 60, 144):
            actual = make_flock()
            for _ in range(fps * 10):
                actual.update(1 / fps)
            for bird, reference in zip(actual.birds, expected.birds):
                self.assertAlmostEqual(bird.x, reference.x, places=7)
                self.assertAlmostEqual(bird.phase, reference.phase, places=7)
                self.assertEqual(bird.direction, reference.direction)


if __name__ == '__main__':
    unittest.main()
