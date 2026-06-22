import getopt
import importlib.metadata
import sys
from collections.abc import Iterable
from dataclasses import dataclass, field
from functools import partial
from typing import Any, Final, Optional, Self

from .SubCommand import SubCommand
from .SuperFlag import SuperFlag
from .SuperParseError import SuperParseError

__all__ = ["SuperParser"]

INDENT: Final[int] = 2
SHIFT: Final[int] = 8
ARGS_MESSAGE: Final[str] = (
    "These remaining args are parsed again by the chosen subcommand."
)


@dataclass
class SuperParser:
    description: object = field(default=None, kw_only=True)
    fromfile_prefix_chars: object = field(default="", kw_only=True)
    helpFlag: SuperFlag = field(
        default_factory=partial(SuperFlag, help="print this message and exit"),
        kw_only=True,
    )
    prog: Optional[str] = field(default=None, kw_only=True)
    subCommands: list[SubCommand] = field(default_factory=list, kw_only=True)
    versionFlag: SuperFlag = field(
        default_factory=partial(SuperFlag, help="print version and exit"),
        kw_only=True,
    )

    def _description(self: Self) -> Optional[str]:
        if self.description is None:
            return None
        else:
            return str(self.description)

    def _keys_message(self: Self) -> Optional[str]:
        ans: str
        help_intro: str
        shift: int
        version_intro: str
        help_intro = self.helpFlag.intro()
        version_intro = self.versionFlag.intro()
        if help_intro + version_intro == "":
            return None
        ans = "keys:"
        shift = max(SHIFT, len(help_intro), len(version_intro))
        shift += INDENT
        if help_intro:
            ans += "\n"
            ans += " " * INDENT
            ans += help_intro.ljust(shift)
            ans += str(self.helpFlag.help)
        if version_intro:
            ans += "\n"
            ans += " " * INDENT
            ans += version_intro.ljust(shift)
            ans += str(self.versionFlag.help)
        return ans

    def _prog(self: Self) -> str:
        if self.prog is None:
            return str(sys.argv[0])
        else:
            return str(self.prog)

    def _subCommands_message(self: Self) -> Optional[str]:
        intros = list(map(SubCommand.intro, self.subCommands))
        if not intros:
            return None
        ans = "subcommands:"
        shift = max(SHIFT, *map(len, intros))
        shift += INDENT
        for intro, cmd in zip(intros, self.subCommands):
            ans += "\n"
            ans += " " * INDENT
            ans += intro.ljust(shift)
            ans += str(cmd.help)
        return ans

    def add_subCommand(self: Self, **kwargs: Any) -> SubCommand:
        self.subCommands.append(SubCommand(**kwargs))
        return self.subCommands[-1]

    def help(self: Self) -> str:
        ans: list[Optional[str]]
        intro = self.helpFlag._message()
        if intro is not None:
            return intro
        ans = list()
        ans.append(self._description())
        ans.append(self.usage())
        ans.append(self._keys_message())
        ans.append(self._subCommands_message())
        ans.append("args:\n" + " " * INDENT + ARGS_MESSAGE)
        filtered = [part for part in ans if part is not None]
        return "\n\n".join(filtered)

    def parse_args(
        self: Self, args: Optional[Iterable[object]] = None, /
    ) -> list[str]:
        args_: list[str]
        cmd: SubCommand
        longopts: tuple[str, ...]
        optitems: list[tuple[str, str]]
        shortopts: str
        args_ = list()
        for arg in map(str, sys.argv[1:] if args is None else args):
            prefix_chars = str(self.fromfile_prefix_chars)
            if arg == "" or arg[0] not in prefix_chars:
                args_.append(arg)
                continue
            with open(arg[1:], "r") as stream:
                args_.extend(stream.read().splitlines())
        shortopts = self.helpFlag.shortopts() + self.versionFlag.shortopts()
        longopts = self.helpFlag.longopts() + self.versionFlag.longopts()
        try:
            optitems, args_ = getopt.getopt(
                args=args_, shortopts=shortopts, longopts=longopts
            )
        except Exception:
            raise SuperParseError("Failed getopt!")
        if set(self.helpFlag._keys()).intersection(dict(optitems).keys()):
            _print(self.help())
            return list()
        if set(self.versionFlag._keys()).intersection(dict(optitems).keys()):
            _print(self.version())
            return list()
        if not args_:
            raise SuperParseError("Subcommand missing!")
        for cmd in self.subCommands:
            if args_[0] == str(cmd.name):
                return args_
        for cmd in self.subCommands:
            if args_[0] in map(str, cmd.aliases):
                args_[0] = str(cmd.name)
                return args_
        raise SuperParseError("Subcommand %r unknown!" % args_[0])

    def usage(self: Self) -> str:
        ans: str
        piece: str
        ans = "usage:"
        ans += " " + self._prog()
        for flag in (self.helpFlag, self.versionFlag):
            piece = flag._usage()
            if piece:
                ans += " "
                ans += piece
        ans += " {"
        ans += ", ".join(map(SubCommand._usage, self.subCommands))
        ans += "} [arg ...]"
        return ans

    def version(self: Self) -> str:
        if self.versionFlag.message is not None:
            return str(self.versionFlag.message)
        else:
            return f"{self._prog()}, version {importlib.metadata.version(self._prog())}"


def _print(value: Optional[str]) -> None:
    if value is not None:
        print(value)
