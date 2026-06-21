import contextlib
import io
import unittest
from typing import Any, Self

from superparsing import SubCommand


def capture_stdout(func: Any, *args: Any, **kwargs: Any) -> Any:
    """Run ``func`` and return (return_value, captured_stdout_str)."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        result = func(*args, **kwargs)
    return result, buf.getvalue()


# ---------------------------------------------------------------------------
# SubCommand
# ---------------------------------------------------------------------------
class TestSubCommand(unittest.TestCase):
    def test_defaults(self: Self) -> None:
        c = SubCommand(name="run")
        self.assertEqual(c.name, "run")
        self.assertEqual(tuple(c.aliases), ())
        self.assertEqual(c.help, "")

    def test_usage_no_aliases(self: Self) -> None:
        self.assertEqual(SubCommand(name="run")._usage(), "run")

    def test_usage_with_aliases(self: Self) -> None:
        c = SubCommand(name="build", aliases=["b", "make"])
        self.assertEqual(c._usage(), "build, b, make")

    def test_usage_coerces_non_strings(self: Self) -> None:
        c = SubCommand(name=1, aliases=[2, 3])
        self.assertEqual(c._usage(), "1, 2, 3")

    def test_intro_no_aliases(self: Self) -> None:
        self.assertEqual(SubCommand(name="run").intro(), "run:")

    def test_intro_with_aliases(self: Self) -> None:
        c = SubCommand(name="build", aliases=["b", "make"])
        self.assertEqual(c.intro(), "build(b, make):")

    def test_intro_single_alias(self: Self) -> None:
        self.assertEqual(
            SubCommand(name="build", aliases=["b"]).intro(), "build(b):"
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
