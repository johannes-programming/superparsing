import unittest
from typing import Any, Self
from unittest.mock import patch

from superparsing import SuperFlag, SuperParser


class TestSuperParser(unittest.TestCase):

    def setUp(self: Self) -> None:
        self.parser = SuperParser(
            prog="tool",
            helpFlag=SuperFlag(keys=["-h", "--help"]),
            versionFlag=SuperFlag(keys=["-v", "--version"]),
        )
        self.parser.add_subCommand(
            name="run", aliases=["r"], help="run command"
        )
        self.parser.add_subCommand(name="test", help="test command")

    @patch("importlib.metadata.version")
    def test_version_default(self: Self, mock_version: Any) -> None:
        mock_version.return_value = "2.0.0"
        parser = SuperParser(prog="tool")
        self.assertEqual(parser.version(), "tool, version 2.0.0")


if __name__ == "__main__":
    unittest.main()
