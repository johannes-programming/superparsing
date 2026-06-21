from collections.abc import Iterable
from dataclasses import dataclass
from typing import Optional, Self

__all__ = ["SuperFlag"]


@dataclass
class SuperFlag:
    keys: Iterable[object] = ()
    help: object = ""
    message: Optional[object] = None

    def _keys(self: Self) -> list[str]:
        return list(map(str, self.keys))

    def _message(self: Self) -> Optional[str]:
        if self.message is None:
            return None
        else:
            return str(self.message)

    def _usage(self: Self) -> str:
        ans: list[str]
        ans = self._keys()
        if ans:
            return "[" + ", ".join(ans) + "]"
        else:
            return ""

    def intro(self: Self) -> str:
        ans: list[str]
        ans = self._keys()
        if ans:
            return ", ".join(ans) + ":"
        else:
            return ""

    def longopts(self: Self) -> tuple[str, ...]:
        ans: list[str]
        ans = list()
        for flag in map(str, self.keys):
            if flag.startswith("--"):
                ans.append(flag[2:].split("=")[0])
        return tuple(ans)

    def shortopts(self: Self) -> str:
        ans: str
        ans = ""
        for flag in map(str, self.keys):
            if len(flag) == 2 and flag[0] == "-":
                ans += flag[1]
        return ans
