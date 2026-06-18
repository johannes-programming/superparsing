import contextlib
import io
import unittest
from collections.abc import Callable
from typing import Self

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

    def test_add_subCommand_returns_and_appends(self: Self) -> None:
        p = SuperParser()
        c = p.add_subCommand(name="run", aliases=["r"], help="go")
        self.assertIsInstance(c, SubCommand)
        self.assertIs(p.subCommands[-1], c)
        self.assertEqual(c.name, "run")

    def test_subcommands_message_none_when_empty(self: Self) -> None:
        self.assertIsNone(SuperParser()._subCommands_message())


if __name__ == "__main__":
    unittest.main(verbosity=2)
