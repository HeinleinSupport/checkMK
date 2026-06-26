#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

"""Site-side helper: write an RRD file with a defined data shape.

Runs *inside* a Checkmk site (``rrdtool`` + ``OMD_ROOT``) via ``Site.python_helper``;
not imported by the test process. Shapes: ``varying`` (smooth curve) and ``gaps``
(curve with a contiguous block of missing samples / NaN).

Usage: ``python3 _rrd_injection_helper.py <shape> <rel_path> <step> <start> <count>``
"""

import math
import os
import sys
from pathlib import Path

import rrdtool  # type: ignore[import-not-found]

_SHAPES = ("varying", "gaps")
_USAGE = "usage: _rrd_injection_helper.py <shape> <rel_path> <step> <start> <count>"
# Push samples to rrdtool in batches: per-sample calls are far too slow, while one
# call with the whole high-density window (~1M points) holds a huge list + argv.
_UPDATE_BATCH = 10_000


def _value(index: int, count: int) -> float:
    """A smoothly varying, always-positive sample value."""
    return 50.0 + 40.0 * math.sin(2.0 * math.pi * index / max(count, 1))


def _is_gap(index: int, count: int, shape: str) -> bool:
    """For the 'gaps' shape, drop a contiguous block in the middle third."""
    return shape == "gaps" and count // 3 <= index < 2 * count // 3


def _resolve_target(rel_path: str) -> Path:
    """Resolve ``rel_path`` under ``OMD_ROOT``, rejecting traversal/absolute escapes."""
    omd_root = Path(os.environ["OMD_ROOT"]).resolve()
    target = (omd_root / rel_path).resolve()
    if not target.is_relative_to(omd_root):
        raise ValueError(f"rel_path {rel_path!r} escapes OMD_ROOT")
    return target


def create_rrd(rrd_path: Path, shape: str, step: int, start: int, count: int) -> None:
    rrd_path.parent.mkdir(parents=True, exist_ok=True)
    # Idempotent: re-seeding an existing service RRD is the documented workflow, so
    # drop any prior file rather than relying on rrdtool create's overwrite behaviour.
    rrd_path.unlink(missing_ok=True)
    rrdtool.create(
        [
            str(rrd_path),
            "--start",
            str(start - step),
            "--step",
            str(step),
            f"DS:value:GAUGE:{step * 2}:0:U",
            f"RRA:AVERAGE:0.5:1:{count}",
        ]
    )
    # Feed samples in bounded batches (gaps omitted, left as NaN), so neither the
    # Python list nor the rrdtool argv grows with the full window size.
    batch: list[str] = []
    for index in range(count):
        if _is_gap(index, count, shape):
            continue
        batch.append(f"{start + index * step}:{_value(index, count):f}")
        if len(batch) >= _UPDATE_BATCH:
            rrdtool.update([str(rrd_path), "-t", "value", *batch])
            batch.clear()
    if batch:
        rrdtool.update([str(rrd_path), "-t", "value", *batch])


def _fail(message: str) -> int:
    print(f"error: {message}\n{_USAGE}", file=sys.stderr)
    return 2


def main() -> int:
    args = sys.argv[1:]
    if len(args) != 5:
        return _fail(f"expected 5 arguments, got {len(args)}: {args}")
    shape, rel_path, step_s, start_s, count_s = args
    if shape not in _SHAPES:
        return _fail(f"unknown shape {shape!r}; expected one of {_SHAPES}")
    try:
        step, start, count = int(step_s), int(start_s), int(count_s)
    except ValueError:
        return _fail(f"step/start/count must be integers, got {step_s!r} {start_s!r} {count_s!r}")
    if step <= 0 or count <= 0:
        return _fail(f"step and count must be positive (step={step}, count={count})")
    try:
        target = _resolve_target(rel_path)
    except ValueError as exc:
        return _fail(str(exc))
    create_rrd(target, shape, step, start, count)
    return 0


if __name__ == "__main__":
    sys.exit(main())
