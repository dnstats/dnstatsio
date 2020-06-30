import unittest

from grading import percent_to_letter


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




    def _grade_helper(self, percent: float, expected_letter: str):
        grade = percent_to_letter(percent)
        self.assertEqual(expected_letter, grade)


if __name__ == '__main__':
    unittest.main()
