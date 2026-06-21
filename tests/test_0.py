import os
import tempfile
import unittest
from typing import Self

from superparsing import SubCommand, SuperFlag, SuperParseError, SuperParser


class TestSuperFlag(unittest.TestCase):

    def test_intro(self: Self) -> None:
        flag = SuperFlag(keys=["-h", "--help"])
        self.assertEqual(flag.intro(), "-h, --help:")

    def test_shortopts(self: Self) -> None:
        flag = SuperFlag(keys=["-h", "-v", "--help"])
        self.assertEqual(flag.shortopts(), "hv")

    def test_longopts(self: Self) -> None:
        flag = SuperFlag(keys=["-h", "--help", "--version=1"])
        self.assertEqual(flag.longopts(), ("help", "version"))


class TestSubCommand(unittest.TestCase):

    def test_intro_without_alias(self: Self) -> None:
        cmd = SubCommand(name="run")
        self.assertEqual(cmd.intro(), "run:")

    def test_intro_with_aliases(self: Self) -> None:
        cmd = SubCommand(name="run", aliases=["r", "execute"])
        self.assertEqual(cmd.intro(), "run(r, execute):")


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

    def test_usage(self: Self) -> None:
        usage = self.parser.usage()
        self.assertIn("usage:", usage)
        self.assertIn("tool", usage)
        self.assertIn("run, r", usage)

    def test_help_output(self: Self) -> None:
        text = self.parser.help()
        self.assertIn("usage:", text)
        self.assertIn("subcommands:", text)
        self.assertIn("args:", text)

    def test_parse_valid_subcommand(self: Self) -> None:
        result = self.parser.parse_args(["run"])
        self.assertEqual(result, ["run"])

    def test_parse_alias(self: Self) -> None:
        result = self.parser.parse_args(["r"])
        self.assertEqual(result, ["run"])

    def test_parse_unknown_subcommand(self: Self) -> None:
        with self.assertRaises(SuperParseError):
            self.parser.parse_args(["unknown"])

    def test_parse_missing_subcommand(self: Self) -> None:
        with self.assertRaises(SuperParseError):
            self.parser.parse_args([])

    def test_version_custom_message(self: Self) -> None:
        parser = SuperParser(
            prog="tool", versionFlag=SuperFlag(message="custom version")
        )
        self.assertEqual(parser.version(), "custom version")

    def test_fromfile_prefix_chars(self: Self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            fname = os.path.join(tmpdir, "a.txt")
            with open(fname, "w") as f:
                f.write("run\narg1\narg2")
            parser = SuperParser(prog="tool", fromfile_prefix_chars="@")
            parser.add_subCommand(name="run")
            result = parser.parse_args([f"@{fname}"])
            self.assertEqual(result, ["run", "arg1", "arg2"])


if __name__ == "__main__":
    unittest.main()
