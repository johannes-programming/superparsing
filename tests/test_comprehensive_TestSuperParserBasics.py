import contextlib
import io
import sys
import unittest
from collections.abc import Callable
from typing import Self
from unittest import mock

from superparsing import SubCommand, SuperParser


def capture_stdout(
    func: Callable[..., object],
    *args: object,
    **kwargs: object,
) -> tuple[object, str]:
    """Run ``func`` and return (return_value, captured_stdout_str)."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        result = func(*args, **kwargs)
    return result, buf.getvalue()


# ---------------------------------------------------------------------------
# SuperParser: construction / introspection
# ---------------------------------------------------------------------------
class TestSuperParserBasics(unittest.TestCase):
    def test_default_flags_have_help_text(self: Self) -> None:
        p = SuperParser()
        self.assertEqual(p.helpFlag.help, "print this message and exit")
        self.assertEqual(p.versionFlag.help, "print version and exit")
        # default flags carry no keys until the user assigns them
        self.assertEqual(tuple(p.helpFlag.keys), ())
        self.assertEqual(tuple(p.versionFlag.keys), ())

    def test_instances_do_not_share_mutable_state(self: Self) -> None:
        # default_factory must produce fresh objects per instance
        p1 = SuperParser()
        p2 = SuperParser()
        self.assertIsNot(p1.helpFlag, p2.helpFlag)
        self.assertIsNot(p1.versionFlag, p2.versionFlag)
        self.assertIsNot(p1.subCommands, p2.subCommands)
        p1.subCommands.append(SubCommand(name="x"))
        self.assertEqual(p2.subCommands, [])

    def test_prog_explicit(self: Self) -> None:
        self.assertEqual(SuperParser(prog="tool")._prog(), "tool")

    def test_prog_defaults_to_argv0(self: Self) -> None:
        with mock.patch.object(sys, "argv", ["myscript.py", "a"]):
            self.assertEqual(SuperParser()._prog(), "myscript.py")

    def test_add_subCommand_returns_and_appends(self: Self) -> None:
        p = SuperParser()
        c = p.add_subCommand(name="run", aliases=["r"], help="go")
        self.assertIsInstance(c, SubCommand)
        self.assertIs(p.subCommands[-1], c)
        self.assertEqual(c.name, "run")

    def test_keys_message_none_when_no_keys(self: Self) -> None:
        self.assertIsNone(SuperParser()._keys_message())

    def test_keys_message_help_only(self: Self) -> None:
        p = SuperParser()
        p.helpFlag.keys = ["-h"]
        msg = p._keys_message()
        self.assertIn("keys:", msg)
        self.assertIn("-h:", msg)
        self.assertIn("print this message and exit", msg)
        self.assertNotIn("print version", msg)

    def test_keys_message_both(self: Self) -> None:
        p = SuperParser()
        p.helpFlag.keys = ["-h", "--help"]
        p.versionFlag.keys = ["-v"]
        msg = p._keys_message()
        self.assertIn("-h, --help:", msg)
        self.assertIn("-v:", msg)

    def test_subcommands_message_none_when_empty(self: Self) -> None:
        self.assertIsNone(SuperParser()._subCommands_message())

    def test_subcommands_message_single(self: Self) -> None:
        p = SuperParser()
        p.add_subCommand(name="run", help="do it")
        msg = p._subCommands_message()
        self.assertIn("subcommands:", msg)
        self.assertIn("run:", msg)
        self.assertIn("do it", msg)

    def test_subcommands_message_multiple_with_aliases(self: Self) -> None:
        p = SuperParser()
        p.add_subCommand(name="build", aliases=["b"], help="build it")
        p.add_subCommand(name="clean", help="clean it")
        msg = p._subCommands_message()
        self.assertIn("build(b):", msg)
        self.assertIn("clean:", msg)


if __name__ == "__main__":
    unittest.main(verbosity=2)
