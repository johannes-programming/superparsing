import contextlib
import io
import unittest
from collections.abc import Callable
from typing import Self

from superparsing import SuperParser


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
# SuperParser: usage / help / version text
# ---------------------------------------------------------------------------
class TestSuperParserText(unittest.TestCase):
    def make(self: Self) -> None:
        p = SuperParser(prog="tool")
        p.helpFlag.keys = ["-h", "--help"]
        p.versionFlag.keys = ["-v", "--version"]
        p.add_subCommand(name="build", aliases=["b"], help="build the project")
        p.add_subCommand(name="clean", help="remove artifacts")
        return p

    def test_usage_full(self: Self) -> None:
        p = self.make()
        self.assertEqual(
            p.usage(),
            "usage: tool [-h, --help] [-v, --version] {build, b, clean} [arg ...]",
        )

    def test_usage_no_flags_no_subcommands(self: Self) -> None:
        p = SuperParser(prog="tool")
        self.assertEqual(p.usage(), "usage: tool {} [arg ...]")

    def test_help_contains_all_sections(self: Self) -> None:
        p = self.make()
        h = p.help()
        self.assertTrue(h.startswith("usage: tool"))
        self.assertIn("keys:", h)
        self.assertIn("subcommands:", h)
        self.assertIn("args:", h)
        # sections separated by blank lines
        self.assertIn("\n\n", h)

    def test_help_message_override(self: Self) -> None:
        p = self.make()
        p.helpFlag.message = "custom help blob"
        self.assertEqual(p.help(), "custom help blob")

    def test_help_omits_missing_sections(self: Self) -> None:
        # no flags, no subcommands -> only usage + args sections
        p = SuperParser(prog="tool")
        h = p.help()
        self.assertIn("usage:", h)
        self.assertIn("args:", h)
        self.assertNotIn("keys:", h)
        self.assertNotIn("subcommands:", h)

    def test_version_from_message(self: Self) -> None:
        p = SuperParser(prog="tool")
        p.versionFlag.message = "tool 2.3.4"
        self.assertEqual(p.version(), "tool 2.3.4")

    def test_version_message_coerced(self: Self) -> None:
        p = SuperParser(prog="tool")
        p.versionFlag.message = 99
        self.assertEqual(p.version(), "99")


if __name__ == "__main__":
    unittest.main(verbosity=2)
