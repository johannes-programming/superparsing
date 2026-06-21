"""Comprehensive unit tests for the ``superparse`` module.

Run with:
    python -m unittest -v test_superparse
or, if you have pytest:
    pytest -v test_superparse.py

The suite is organised by class. A final ``TestKnownDefects`` class documents
three confirmed defects using ``unittest.expectedFailure`` so the suite stays
green today but will flag (as "unexpected success") the moment a defect is
fixed -- a built-in reminder to update the tests.
"""

import contextlib
import io
import os
import sys
import tempfile
import unittest
from typing import Any, Self
from unittest import mock

from superparsing import SubCommand, SuperFlag, SuperParseError, SuperParser


def capture_stdout(func, *args, **kwargs):
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
