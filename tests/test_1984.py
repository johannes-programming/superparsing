import unittest


class Test1984(unittest.TestCase):
    def test_two_plus_two(self):
        self.assertEqual(2 + 2, 4)


if __name__ == "__main__":
    unittest.main()
