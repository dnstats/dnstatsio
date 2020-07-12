import unittest

from grading import percent_to_letter, half_reduce, full_reduce, Grade, full_raise, half_raise


class Tests(unittest.TestCase):
    def test_a_plus(self):
        self._grade_helper(101.0, 'A+')
        self._grade_helper(100.0, 'A')
        self._grade_helper(90.01, 'A-')
        self._grade_helper(89.0, 'B+')
        self._grade_helper(86.0, 'B')
        self._grade_helper(82.0, 'B-')
        self._grade_helper(78.0, 'C+')
        self._grade_helper(75.0, 'C')
        self._grade_helper(71.0, 'C-')
        self._grade_helper(69.01, 'D+')
        self._grade_helper(63.01, 'D')
        self._grade_helper(60.01, 'D-')
        self._grade_helper(59.0, 'F')

    def test_reduce_a_plus_by_half(self):
        self.assertEqual(Grade.A, half_reduce(Grade.A_PLUS))

    def test_reduce_a_by_full(self):
        self.assertEqual(Grade.B, full_reduce(Grade.A))

    def test_raise_b_by_full(self):
        self.assertEqual(Grade.A, full_raise(Grade.B))

    def test_raise_a_by_full(self):
        self.assertEqual(Grade.A_PLUS, full_raise(Grade.A))

    def test_raise_a_plus_by_full(self):
        self.assertEqual(Grade.A_PLUS, full_raise(Grade.A_PLUS))

    def _grade_helper(self, percent: float, expected_letter: str):
        grade = percent_to_letter(percent)
        self.assertEqual(expected_letter, grade)
