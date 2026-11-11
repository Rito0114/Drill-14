"""실행: python -m unittest -v (그래픽 창 없이 핵심 동작 검증)."""

import unittest

from bird import ANIMATION_FPS, FRAME_COUNT, Bird, frame_rectangle


class BirdTests(unittest.TestCase):
    def make_bird(self, **overrides):
        values = dict(x=300.0, y=200.0, speed=177.0, direction=1,
                      left=100.0, right=1100.0, phase=0.25)
        values.update(overrides)
        return Bird(**values)

    def test_motion_and_animation_independent_of_render_fps(self):
        results = []
        for fps in (30, 60, 144):
            bird = self.make_bird()
            for _ in range(fps * 10):
                bird.update(1 / fps)
                self.assertLessEqual(bird.left, bird.x)
                self.assertLessEqual(bird.x, bird.right)
            results.append(bird)
        expected = self.make_bird()
        expected.update(10)
        for bird in results:
            self.assertAlmostEqual(bird.x, expected.x, places=7)
            self.assertAlmostEqual(bird.phase, expected.phase, places=7)
            self.assertEqual(bird.direction, expected.direction)
            self.assertEqual(bird.frame, expected.frame)

    def test_right_and_left_reflection_preserve_overshoot(self):
        right = self.make_bird(x=1095, speed=20)
        right.update(1)
        self.assertEqual((right.x, right.direction), (1085, -1))
        left = self.make_bird(x=105, speed=20, direction=-1)
        left.update(1)
        self.assertEqual((left.x, left.direction), (115, 1))

    def test_large_delta_crosses_multiple_boundaries(self):
        bird = self.make_bird(x=100, speed=200)
        bird.update(1000.25)  # 100번 왕복하고 50픽셀 전진
        self.assertEqual((bird.x, bird.direction), (150, 1))

    def test_exact_cycle_returns_to_first_frame_at_30fps(self):
        bird = self.make_bird(phase=0)
        for _ in range(35):  # 35/30초 × 12fps = 정확히 14프레임
            bird.update(1 / 30)
        self.assertEqual(bird.frame, 0)

    def test_fourteen_frames_and_source_coordinate_conversion(self):
        bird = self.make_bird(phase=0)
        visited = []
        for _ in range(FRAME_COUNT):
            visited.append(bird.frame)
            bird.update(1 / ANIMATION_FPS)
        self.assertEqual(visited, list(range(14)))
        self.assertEqual(bird.frame, 0)
        self.assertEqual(frame_rectangle(0, 918, 506), (0, 336, 183, 170))
        self.assertEqual(frame_rectangle(5, 918, 506), (0, 166, 183, 170))
        self.assertEqual(frame_rectangle(13, 918, 506), (550, 0, 184, 166))
        with self.assertRaises(ValueError):
            frame_rectangle(14, 918, 506)
        for frame in range(14):
            x, y, width, height = frame_rectangle(frame, 918, 506)
            self.assertGreaterEqual(min(x, y), 0)
            self.assertLessEqual(x + width, 918)
            self.assertLessEqual(y + height, 506)

    def test_zero_delta_keeps_position_and_phase(self):
        bird = self.make_bird(direction=-1)
        before = bird.x, bird.phase, bird.direction
        bird.update(0)
        self.assertEqual((bird.x, bird.phase, bird.direction), before)

    def test_left_flight_flips_the_same_shared_image(self):
        class RecordingImage:
            w, h = 918, 506

            def clip_composite_draw(self, *args):
                self.args = args

        image = RecordingImage()
        bird = self.make_bird(direction=-1)
        bird.draw(image)
        self.assertEqual(image.args[5], 'h')
        bird.direction = 1
        bird.draw(image)
        self.assertEqual(image.args[5], '')


if __name__ == '__main__':
    unittest.main()
