import unittest
import tempfile
import os

from superparsing import (
    SuperFlag,
    SubCommand,
    SuperParser,
    SuperParseError,
)


class TestSuperFlag(unittest.TestCase):

    def test_keys(self):
        flag = SuperFlag(keys=["-h", "--help"])
        self.assertEqual(flag._keys(), ["-h", "--help"])

    def test_message_none(self):
        flag = SuperFlag()
        self.assertIsNone(flag._message())

    def test_message_str(self):
        flag = SuperFlag(message=123)
        self.assertEqual(flag._message(), "123")

    def test_usage(self):
        flag = SuperFlag(keys=["-h", "--help"])
        self.assertEqual(flag._usage(), "[-h, --help]")

    def test_usage_empty(self):
        flag = SuperFlag()
        self.assertEqual(flag._usage(), "")

    def test_intro(self):
        flag = SuperFlag(keys=["-h", "--help"])
        self.assertEqual(flag.intro(), "-h, --help:")

    def test_shortopts(self):
        flag = SuperFlag(keys=["-h", "-v", "--help"])
        self.assertEqual(flag.shortopts(), "hv")

    def test_longopts(self):
        flag = SuperFlag(keys=["-h", "--help", "--version=1"])
        self.assertEqual(flag.longopts(), ("help", "version"))


class TestSubCommand(unittest.TestCase):

    def test_usage(self):
        cmd = SubCommand(name="run", aliases=["r"])
        self.assertEqual(cmd._usage(), "run, r")

    def test_intro_without_alias(self):
        cmd = SubCommand(name="run")
        self.assertEqual(cmd.intro(), "run:")

    def test_intro_with_aliases(self):
        cmd = SubCommand(name="run", aliases=["r", "execute"])
        self.assertEqual(cmd.intro(), "run(r, execute):")


class TestSuperParser(unittest.TestCase):

    def setUp(self):
        self.parser = SuperParser(
            prog="tool",
            helpFlag=SuperFlag(keys=["-h", "--help"]),
            versionFlag=SuperFlag(keys=["-v", "--version"])
        )
        self.parser.add_subCommand(name="run", aliases=["r"], help="run command")
        self.parser.add_subCommand(name="test", help="test command")

    def test_prog(self):
        self.assertEqual(self.parser._prog(), "tool")

    def test_usage(self):
        usage = self.parser.usage()
        self.assertIn("usage:", usage)
        self.assertIn("tool", usage)
        self.assertIn("run, r", usage)

    def test_help_output(self):
        text = self.parser.help()
        self.assertIn("usage:", text)
        self.assertIn("subcommands:", text)
        self.assertIn("args:", text)

    def test_parse_valid_subcommand(self):
        result = self.parser.parse_args(["run"])
        self.assertEqual(result, ["run"])

    def test_parse_alias(self):
        result = self.parser.parse_args(["r"])
        self.assertEqual(result, ["run"])

    def test_parse_unknown_subcommand(self):
        with self.assertRaises(SuperParseError):
            self.parser.parse_args(["unknown"])

    def test_parse_missing_subcommand(self):
        with self.assertRaises(SuperParseError):
            self.parser.parse_args([])


    def test_version_custom_message(self):
        parser = SuperParser(
            prog="tool",
            versionFlag=SuperFlag(message="custom version")
        )
        self.assertEqual(parser.version(), "custom version")


    def test_fromfile_prefix_chars(self):
        with tempfile.NamedTemporaryFile("w", delete=False) as f:
            f.write("run\narg1\narg2")
            fname = f.name

        try:
            parser = SuperParser(
                prog="tool",
                fromfile_prefix_chars="@"
            )
            parser.add_subCommand(name="run")

            result = parser.parse_args([f"@{fname}"])
            self.assertEqual(result, ["run", "arg1", "arg2"])
        finally:
            os.unlink(fname)

    def test_subcommands_message(self):
        msg = self.parser._subCommands_message()
        self.assertIn("subcommands:", msg)
        self.assertIn("run", msg)

    def test_keys_message(self):
        msg = self.parser._keys_message()
        self.assertIn("keys:", msg)


if __name__ == "__main__":
    unittest.main()