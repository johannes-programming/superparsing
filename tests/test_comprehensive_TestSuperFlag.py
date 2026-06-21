import contextlib
import io
import unittest
from typing import Any, Self

from superparsing import SuperFlag


def capture_stdout(func: Any, *args: Any, **kwargs: Any) -> Any:
    """Run ``func`` and return (return_value, captured_stdout_str)."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        result = func(*args, **kwargs)
    return result, buf.getvalue()


# ---------------------------------------------------------------------------
# SuperFlag
# ---------------------------------------------------------------------------
class TestSuperFlag(unittest.TestCase):
    def test_defaults(self: Self) -> None:
        f = SuperFlag()
        self.assertEqual(tuple(f.keys), ())
        self.assertEqual(f.help, "")
        self.assertIsNone(f.message)

    def test_keys_stringifies(self: Self) -> None:
        f = SuperFlag(keys=["-h", "--help"])
        self.assertEqual(f._keys(), ["-h", "--help"])

    def test_keys_stringifies_non_strings(self: Self) -> None:
        # keys is typed Iterable[object]; non-strings must be coerced via str()
        f = SuperFlag(keys=[1, 2.5, None])
        self.assertEqual(f._keys(), ["1", "2.5", "None"])

    def test_message_none(self: Self) -> None:
        self.assertIsNone(SuperFlag().message)
        self.assertIsNone(SuperFlag()._message())

    def test_message_coerced(self: Self) -> None:
        self.assertEqual(SuperFlag(message=42)._message(), "42")
        self.assertEqual(SuperFlag(message="hi")._message(), "hi")

    def test_usage_with_keys(self: Self) -> None:
        self.assertEqual(
            SuperFlag(keys=["-h", "--help"])._usage(), "[-h, --help]"
        )

    def test_usage_empty(self: Self) -> None:
        self.assertEqual(SuperFlag()._usage(), "")

    def test_intro_with_keys(self: Self) -> None:
        self.assertEqual(
            SuperFlag(keys=["-h", "--help"]).intro(), "-h, --help:"
        )

    def test_intro_empty(self: Self) -> None:
        self.assertEqual(SuperFlag().intro(), "")

    def test_longopts(self: Self) -> None:
        f = SuperFlag(keys=["-h", "--help", "--version"])
        self.assertEqual(f.longopts(), ("help", "version"))

    def test_longopts_strips_equals(self: Self) -> None:
        f = SuperFlag(keys=["--name=VALUE"])
        self.assertEqual(f.longopts(), ("name",))

    def test_longopts_ignores_short_and_bare(self: Self) -> None:
        f = SuperFlag(keys=["-h", "h", "help", "--x"])
        self.assertEqual(f.longopts(), ("x",))

    def test_shortopts(self: Self) -> None:
        f = SuperFlag(keys=["-h", "-v", "--help"])
        self.assertEqual(f.shortopts(), "hv")

    def test_shortopts_ignores_long_and_malformed(self: Self) -> None:
        f = SuperFlag(keys=["--help", "-ab", "x", "-"])
        # only exactly "-X" (len 2, leading dash) counts
        self.assertEqual(f.shortopts(), "")


if __name__ == "__main__":
    unittest.main(verbosity=2)
