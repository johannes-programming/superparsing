from collections.abc import Iterable
from dataclasses import dataclass
from typing import Self

__all__ = ["SubCommand"]


@dataclass
class SubCommand:
    name: object
    aliases: Iterable[object] = ()
    help: object = ""

    def _usage(self: Self) -> str:
        return ", ".join(map(str, [self.name] + list(self.aliases)))

    def intro(self: Self) -> str:
        ans: str
        aliases_: list[str]
        aliases_ = list(map(str, self.aliases))
        ans = str(self.name)
        if not aliases_:
            return ans + ":"
        ans += "("
        ans += ", ".join(aliases_)
        ans += "):"
        return ans
