

import contextlib
import io
import unittest
from typing import Self

from superparsing import SuperParseError, SuperParser


def capture_stdout(func, *args, **kwargs):
    """Run ``func`` and return (return_value, captured_stdout_str)."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        result = func(*args, **kwargs)
    return result, buf.getvalue()


# ---------------------------------------------------------------------------
# Known defects (documented as expected failures)
# ---------------------------------------------------------------------------
class TestKnownDefects(unittest.TestCase):
    """Each test asserts the *desired* behaviour. They are expected to fail
    against the current code; fixing a defect turns the corresponding test
    into an 'unexpected success', prompting you to drop the decorator."""

    @unittest.expectedFailure
    def test_defect_a_non_string_keys_should_be_detected(self: Self) -> None:
        # parse_args compares RAW keys to getopt's string output instead of
        # using SuperFlag._keys(); non-string keys silently fail to match.
        class K:
            def __init__(self, s) -> None:
                self.s = s

            def __str__(self: Self) -> None:
                return self.s

        p = SuperParser(prog="tool")
        p.helpFlag.keys = [K("-h")]
        p.add_subCommand(name="run")
        result, out = capture_stdout(p.parse_args, ["-h"])
        self.assertEqual(result, [])
        self.assertIn("usage:", out)

    @unittest.expectedFailure
    def test_defect_b_default_version_should_not_crash(self: Self) -> None:
        # With no versionFlag.message and prog not an installed distribution,
        # version() raises importlib.metadata.PackageNotFoundError.
        p = SuperParser(prog="definitely-not-an-installed-package-xyz")
        # desired: returns a string rather than raising
        self.assertIsInstance(p.version(), str)

    @unittest.expectedFailure
    def test_defect_c_getopt_error_should_be_wrapped(self: Self) -> None:
        # An unknown option leaks getopt.GetoptError rather than the module's
        # own SuperParseError, breaking the parser's error contract.
        p = SuperParser(prog="tool")
        p.helpFlag.keys = ["-h"]
        p.add_subCommand(name="run")
        with self.assertRaises(SuperParseError):
            p.parse_args(["-x"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
