"""FIDELIO — an offline OPSEC / digital-footprint self-audit.

Named after Beethoven's only opera: a story about a hidden identity held for
years, and about being faithful to oneself. FIDELIO asks the hard questions,
scores your exposure across the categories that together make a footprint, and
turns the answers into a remediation roadmap — all offline, nothing leaves the
machine.

Honesty first: FIDELIO scores *habits*, not identities. A perfect score is a
discipline, never a proof of anonymity.
"""

from __future__ import annotations

__version__ = "0.1.0"

BANNER = r"""
  ______ ____  ____   ___  __      __ ____
 |  ____|  _ \|  _ \ / _ \ \ \    / / ____|
 | |__  | |_) | | | | | | | \ \  /\ / /_  |
 |  __| |  _ <| |_| | |_| |  \ V  V /  _| |
 |_|    |_| \_\\____/ \___/    \_/\_/  |_|

 the faithful look on — an OPSEC self-audit
"""

__all__ = ["BANNER", "__version__"]
