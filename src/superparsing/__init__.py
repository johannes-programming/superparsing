from typing import Self, Optional, Final, Any
from collections.abc import Iterable
from dataclasses import dataclass, field
import sys
import getopt
import importlib.metadata
from functools import partial

INDENT :Final[int] = 2
SHIFT :Final[int] = 8
ARGS_MESSAGE:Final[str] = "These remaining args are parsed again by the chosen subcommand."



class SuperParseError(ValueError):pass

@dataclass
class SuperFlag:
    keys:Iterable[object] = ()
    help:object = ""
    message:Optional[object] = None

    def _keys(self:Self) -> list[str]:
        return list(map(str, self.keys))
    def _message(self:Self) -> Optional[str]:
        if self.message is None:
            return None
        else:
            return str(self.message)
    def _usage(self:Self) -> str:
        ans:list[str]
        ans = self._keys()
        if ans:
            return "[" + ", ".join(ans) + "]"
        else:
            return ""
        
    def intro(self:Self) -> str:
        ans:list[str]
        ans = self._keys()
        if ans:
            return ", ".join(ans) + ":"
        else:
            return ""
    
    def longopts(self:Self) -> tuple[str, ...]:
        ans:list[str]
        ans =list()
        for flag in map(str, self.keys):
            if flag.startswith("--"):
                ans.append(flag[2:].split("=")[0])
        return tuple(ans)
    def shortopts(self:Self) -> str:
        ans:str
        ans=""
        for flag in map(str, self.keys):
            if len(flag) == 2 and flag[0] == "-":
                ans += flag[1]
        return ans

@dataclass
class SubCommand:
    name:object
    aliases:Iterable[object] = ()
    help:object = ""
    def _usage(self:Self)-> str:
        return ", ".join(map(str, [self.name]+list(self.aliases)))
    def intro(self:Self) -> str:
        ans:str
        aliases_:list[str]
        aliases_=list(map(str, self.aliases))
        ans = str(self.name)
        if not aliases_:
            return ans + ":"
        ans += "("
        ans += ", ".join(aliases_)
        ans+="):"
        return ans
    

        

        


@dataclass
class SuperParser:
    fromfile_prefix_chars:object = field(default="", kw_only=True)
    helpFlag:SuperFlag = field(default_factory=partial(SuperFlag, help="print this message and exit"), kw_only=True)
    prog:Optional[str] = field(default=None, kw_only=True)
    subCommands:list[SubCommand] = field(default_factory=list, kw_only=True)
    versionFlag:SuperFlag = field(default_factory=partial(SuperFlag, help="print version and exit"), kw_only=True)
    
    def _keys_message(self:Self)->Optional[str]:
        ans:str
        shift:int
        help_intro = self.helpFlag.intro()
        version_intro = self.versionFlag.intro()
        if help_intro + version_intro == "":
            return None
        ans="keys:"
        shift = max(SHIFT, len(help_intro), len(version_intro))
        shift += INDENT
        if help_intro:
            ans +="\n"
            ans+= " " * INDENT 
            ans+= help_intro.ljust(shift)
            ans+= str(self.helpFlag.help)
        if version_intro:
            ans +="\n"
            ans+= " " * INDENT 
            ans+= version_intro.ljust(shift)
            ans+= str(self.versionFlag.help)
        return ans
    
    
    def _prog(self:Self) -> str:
        if self.prog is None:
            return str(sys.argv[0])
        else:
            return str(self.prog)
        
    def _subCommands_message(self:Self)->Optional[str]:
        intros=list(map(SubCommand.intro, self.subCommands))
        if not intros:
            return None
        ans = "subcommands:"
        shift = max(SHIFT, *map(len, intros)) 
        shift+= INDENT
        for intro, cmd in zip(intros, self.subCommands):
            ans+="\n" + " " * INDENT + intro.ljust(shift) + str(cmd.help)
        return ans
    
    def add_subCommand(self:Self, **kwargs:Any) -> SubCommand:
        self.subCommands.append(SubCommand(**kwargs))
        return self.subCommands[-1]

        
    
    def help(self:Self)->str:
        ans:list[Optional[str]]
        intro = self.helpFlag._message()
        if intro is not None:
            return intro
        ans = list()
        ans.append(self.usage())
        ans.append(self._keys_message())
        ans.append(self._subCommands_message())
        ans.append("args:\n" + " "*INDENT +ARGS_MESSAGE)
        while None in ans:
            ans.remove(None)
        return "\n\n".join(ans)
        

        

    
    def parse_args(self:Self, args:Optional[Iterable[str]]=None, /)->list[str]:
        args_:list[str]
        cmd:SubCommand
        longopts:tuple[str, ...]
        optitems:list[tuple[str, str]]
        shortopts:str
        args_=list()
        for arg in map(str, sys.argv[1:] if args is None else args):
            if arg == "" or arg[0] not in self.fromfile_prefix_chars:
                args_.append(arg)
                continue
            with open(arg[1:], "r") as stream:
                args_.extend(stream.read().splitlines())
        shortopts=self.helpFlag.shortopts() + self.versionFlag.shortopts()
        longopts=self.helpFlag.longopts() + self.versionFlag.longopts()
        optitems, args_ = getopt.getopt(args=args_, shortopts=shortopts, longopts=longopts)
        if set(self.helpFlag.keys).intersection(dict(optitems).keys()):
            _print(self.help())
            return list()
        if set(self.versionFlag.keys).intersection(dict(optitems).keys()):
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
        
        
            
    def usage(self:Self) -> str:
        ans :str
        piece:str
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
        
    def version(self:Self)->str:
        if self.versionFlag.message is not None:
            return str(self.versionFlag.message)
        else:
            return f"{self._prog()}, version {importlib.metadata.version(self._prog())}" 




def _print(value:Optional[str]) -> None:
    if value is not None:
        print(value)