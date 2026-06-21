import unittest
from unittest.mock import patch


from superparsing import (
    SuperFlag,
    SuperParser,
)


class TestSuperParser(unittest.TestCase):

    def setUp(self):
        self.parser = SuperParser(
            prog="tool",
            helpFlag=SuperFlag(keys=["-h", "--help"]),
            versionFlag=SuperFlag(keys=["-v", "--version"])
        )
        self.parser.add_subCommand(name="run", aliases=["r"], help="run command")
        self.parser.add_subCommand(name="test", help="test command")

    @patch("superparser._print")
    def test_help_flag(self, mock_print):
        result = self.parser.parse_args(["--help"])
        self.assertEqual(result, [])
        mock_print.assert_called_once()

    @patch("superparser._print")
    def test_version_flag(self, mock_print):
        with patch.object(self.parser, "version", return_value="1.0.0"):
            result = self.parser.parse_args(["--version"])
            self.assertEqual(result, [])
            mock_print.assert_called_once_with("1.0.0")

    @patch("importlib.metadata.version")
    def test_version_default(self, mock_version):
        mock_version.return_value = "2.0.0"
        parser = SuperParser(prog="tool")
        self.assertEqual(parser.version(), "tool, version 2.0.0")

if __name__ == "__main__":
    unittest.main()