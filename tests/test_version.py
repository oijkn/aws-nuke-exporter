import unittest

from aws_nuke_exporter import __version__


class TestVersion(unittest.TestCase):

    def test_version(self):
        """Test that the package version is correct."""
        expected_version = "1.0.2"
        self.assertEqual(__version__, expected_version)


if __name__ == '__main__':
    unittest.main()
