"""python -m clampform report | verify <program> <part> <chuck> | audit07"""

from __future__ import annotations

import argparse
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="clampform")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("report", help="all parts -> reports/, reports/nc/, docs/img/")
    r.add_argument("--out", default=None)
    r.add_argument("--no-figures", action="store_true")
    r.add_argument("--fast", action="store_true", help="skip the sensitivity study")
    r.add_argument("--parts", nargs="*", default=None)
    v = sub.add_parser("verify", help="read a program back and check the workholding physics")
    v.add_argument("program")
    v.add_argument("part")
    v.add_argument("chuck", nargs="?", choices=["3J", "6J", "PIE"], help="default: the chuck named in the program header")
    v.add_argument("--no-fe", action="store_true", help="skip the roundness check (no FE model)")
    sub.add_parser("audit07", help="speed-limit audit of the project 07 programs in data/p07")
    a = ap.parse_args(argv)
    if a.cmd == "report":
        from .report import run

        run(Path(a.out) if a.out else None, figs=not a.no_figures, parts=a.parts, fast=a.fast)
        return 0
    if a.cmd == "verify":
        from .form import PartFE
        from .parts import load_parts
        from .process import chuck_for
        from .verify import verify

        import re

        p = load_parts()[a.part]
        text = Path(a.program).read_text(encoding="utf-8")
        chuck = a.chuck or re.search(r"CHUCK (3J|6J|PIE)-", text, re.I).group(1).upper()
        fe = None if a.no_fe else PartFE(p, chuck_for(p, chuck).grip_len)
        res = verify(text, p, chuck, fe)
        for f in res.findings:
            print(f"{f.rule} line {f.line}: {f.msg}")
        print(f"{'PASS' if res.ok else 'FINDINGS'}: {len(res.blocks)} cutting blocks, max {res.max_rpm:.0f} rpm, min grip {res.min_grip:.2f}")
        return 0 if res.ok else 1
    if a.cmd == "audit07":
        from .report import audit_section

        print(audit_section()[0])
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
