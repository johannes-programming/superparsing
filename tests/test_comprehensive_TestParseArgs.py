import contextlib
import io
import os
import sys
import tempfile
import unittest
from typing import Any, Self
from unittest import mock

from superparsing import SuperParseError, SuperParser


def capture_stdout(func: Any, *args: Any, **kwargs: Any) -> Any:
    """Run ``func`` and return (return_value, captured_stdout_str)."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        result = func(*args, **kwargs)
    return result, buf.getvalue()


# ---------------------------------------------------------------------------
# SuperParser: parse_args
# ---------------------------------------------------------------------------
class TestParseArgs(unittest.TestCase):
    def make(self: Self) -> None:
        p = SuperParser(prog="tool")
        p.helpFlag.keys = ["-h", "--help"]
        p.versionFlag.keys = ["-v", "--version"]
        p.versionFlag.message = "tool 1.0"
        p.add_subCommand(name="build", aliases=["b", "mk"], help="build")
        p.add_subCommand(name="clean", help="clean")
        return p

    def test_plain_subcommand(self: Self) -> None:
        p = self.make()
        self.assertEqual(p.parse_args(["build"]), ["build"])

    def test_subcommand_with_trailing_args(self: Self) -> None:
        p = self.make()
        self.assertEqual(
            p.parse_args(["build", "--force", "target"]),
            ["build", "--force", "target"],
        )

    def test_alias_is_rewritten_to_canonical_name(self: Self) -> None:
        p = self.make()
        self.assertEqual(p.parse_args(["b", "x"]), ["build", "x"])
        self.assertEqual(p.parse_args(["mk"]), ["build"])

    def test_getopt_stops_at_first_positional(self: Self) -> None:
        # flags after the subcommand are passed through, NOT consumed as help
        p = self.make()
        _, out = capture_stdout(p.parse_args, ["build", "-h"])
        # parse_args returns the list (help not triggered)
        self.assertEqual(p.parse_args(["build", "-h"]), ["build", "-h"])
        self.assertEqual(out, "")

    def test_help_short_flag_prints_and_returns_empty(self: Self) -> None:
        p = self.make()
        result, out = capture_stdout(p.parse_args, ["-h"])
        self.assertEqual(result, [])
        self.assertIn("usage: tool", out)

    def test_help_long_flag(self: Self) -> None:
        p = self.make()
        result, out = capture_stdout(p.parse_args, ["--help"])
        self.assertEqual(result, [])
        self.assertIn("subcommands:", out)

    def test_version_flag_prints_and_returns_empty(self: Self) -> None:
        p = self.make()
        result, out = capture_stdout(p.parse_args, ["-v"])
        self.assertEqual(result, [])
        self.assertEqual(out.strip(), "tool 1.0")

    def test_help_takes_precedence_over_version(self: Self) -> None:
        p = self.make()
        result, out = capture_stdout(p.parse_args, ["-v", "-h"])
        self.assertEqual(result, [])
        self.assertIn("usage:", out)
        self.assertNotIn("tool 1.0", out)

    def test_missing_subcommand_raises(self: Self) -> None:
        p = self.make()
        with self.assertRaises(SuperParseError) as ctx:
            p.parse_args([])
        self.assertIn("Subcommand missing", str(ctx.exception))

    def test_unknown_subcommand_raises(self: Self) -> None:
        p = self.make()
        with self.assertRaises(SuperParseError) as ctx:
            p.parse_args(["nope"])
        self.assertIn("unknown", str(ctx.exception))

    def test_reads_sys_argv_when_args_none(self: Self) -> None:
        p = self.make()
        with mock.patch.object(sys, "argv", ["tool", "clean", "now"]):
            self.assertEqual(p.parse_args(), ["clean", "now"])

    def test_non_string_args_are_coerced(self: Self) -> None:
        p = self.make()
        # map(str, ...) means numeric tokens are stringified before matching
        self.assertEqual(p.parse_args(["build", 5]), ["build", "5"])

    def test_fromfile_prefix_expands_file(self: Self) -> None:
        p = self.make()
        p.fromfile_prefix_chars = "@"
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "args.txt")
            with open(path, "w") as fh:
                fh.write("build\n--flag\nvalue\n")
            self.assertEqual(
                p.parse_args(["@" + path]),
                ["build", "--flag", "value"],
            )

    def test_fromfile_disabled_by_default(self: Self) -> None:
        # default fromfile_prefix_chars == "" -> "@file" treated literally
        p = self.make()
        with self.assertRaises(SuperParseError):
            # "@whatever" is an unknown subcommand, not a file read
            p.parse_args(["@whatever"])

    def test_empty_string_arg_is_not_treated_as_file(self: Self) -> None:
        p = self.make()
        p.fromfile_prefix_chars = "@"
        # leading "" must not crash on arg[0]; it's a positional/unknown subcmd
        with self.assertRaises(SuperParseError):
            p.parse_args([""])


if __name__ == "__main__":
    unittest.main(verbosity=2)
