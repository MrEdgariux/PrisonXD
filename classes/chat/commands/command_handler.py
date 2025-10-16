from dataclasses import dataclass
from typing import Callable, Dict, List, Any

@dataclass
class CommandContext:
    player: Any
    scene_mgr: Any
    notifier: Any
    chat: Any
    shop_ui: Any = None
    shop_mgr: Any = None
    config: Any = None
    debug: Any = None

class CommandRegistry:
    def __init__(self):
        self._cmds: Dict[str, Callable[[CommandContext, List[str]], None]] = {}

    def register(self, name: str, func: Callable[[CommandContext, List[str]], None], *, aliases: List[str] = None):
        self._cmds[name] = func
        if aliases:
            for a in aliases:
                self._cmds[a] = func

    def run(self, ctx: CommandContext, raw: str):
        """
        raw is the command line WITHOUT the leading slash.
        Supports quoted args: /give "iron ore" 10
        """
        parts = self._split_argv(raw)
        if not parts:
            return
        cmd, *args = parts
        func = self._cmds.get(cmd.lower())
        if not func:
            self._feedback(ctx, f"Unknown command: {cmd}. Try /help", level="warning")
            return
        try:
            func(ctx, args)
        except Exception as e:
            self._feedback(ctx, f"Command error: {e}", level="error")

    def _split_argv(self, s: str) -> List[str]:
        # minimal argv splitter that respects "quoted strings"
        out, buf, in_quotes = [], "", False
        for ch in s.strip():
            if ch == '"' and not in_quotes:
                in_quotes = True
            elif ch == '"' and in_quotes:
                in_quotes = False
            elif ch.isspace() and not in_quotes:
                if buf:
                    out.append(buf); buf = ""
            else:
                buf += ch
        if buf:
            out.append(buf)
        return out

    def _feedback(self, ctx: CommandContext, msg: str, level="info"):
        if ctx.notifier:
            ctx.notifier.push(msg, level=level)
        if ctx.chat:
            ctx.chat.add_message("System", msg)