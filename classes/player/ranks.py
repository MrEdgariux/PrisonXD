# classes/player/ranks.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

@dataclass
class Rank:
    id: str
    display_name: str
    price: int                       # money required to rank up into this rank
    color: Tuple[int,int,int] = (255,255,255)
    order: int = 0                   # 0=lowest
    req_gems: int = 0                # optional: gems required
    req_blocks: int = 0              # optional: blocks mined required

class RankManager:
    def __init__(self):
        self._ranks: Dict[str, Rank] = {}
        self._ordered: List[Rank] = []

    def register(self, rank: Rank):
        self._ranks[rank.id] = rank
        self._reindex()

    def bulk_register(self, ranks: List[Rank]):
        for r in ranks:
            self._ranks[r.id] = r
        self._reindex()

    def _reindex(self):
        self._ordered = sorted(self._ranks.values(), key=lambda r: r.order)

    def get(self, id: str) -> Optional[Rank]:
        return self._ranks.get(id)

    def all(self) -> List[Rank]:
        return list(self._ordered)

    def next_after(self, current_id: str) -> Optional[Rank]:
        """Next rank by order, or None if at top."""
        if current_id not in self._ranks:
            return None
        cur = self._ranks[current_id]
        for r in self._ordered:
            if r.order > cur.order:
                return r
        return None

    # --- rank-up helpers ---
    def can_rank_up(self, player) -> Tuple[bool, str, Optional[Rank]]:
        """Check if player can rank up; returns (ok, reason, next_rank)."""
        if not getattr(player, "rank", None):
            return False, "You have no current rank.", None
        nxt = self.next_after(player.rank.id)
        if not nxt:
            return False, "You are at the max rank.", None

        # money
        if getattr(player, "money", 0) < nxt.price:
            return False, f"Need ${nxt.price} to rank up.", nxt
        # gems
        if getattr(player, "gems", 0) < nxt.req_gems:
            return False, f"Need {nxt.req_gems} gems to rank up.", nxt
        # blocks mined
        blocks = player.stats.get("blocks_mined", 0) if hasattr(player, "stats") else 0
        if blocks < nxt.req_blocks:
            return False, f"Mine {nxt.req_blocks} blocks to rank up (you have {blocks}).", nxt

        return True, "OK", nxt

    def do_rank_up(self, player, notifier=None) -> Tuple[bool, str]:
        ok, reason, nxt = self.can_rank_up(player)
        if not ok or not nxt:
            return False, reason

        # pay costs
        player.money -= nxt.price
        if nxt.req_gems:
            player.gems -= nxt.req_gems

        # set new rank
        player.rank = nxt
        if notifier:
            notifier.push(f"Ranked up to {nxt.display_name}!", level="success")
        return True, f"Welcome to {nxt.display_name}!"
