import unittest


class BasicTest(unittest.TestCase):
    def test_sanity(self):
        self.assertTrue(1 + 1 == 2)


if __name__ == "__main__":
    unittest.main()
