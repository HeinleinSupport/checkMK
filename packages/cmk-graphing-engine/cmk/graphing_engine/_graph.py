#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from __future__ import annotations

import itertools
from collections.abc import Sequence
from dataclasses import dataclass

from ._quantities import Quantity, RRDMetric
from ._units import CurveAttributes

type Bound = int | float | Quantity


@dataclass(frozen=True)
class MinimalRange:
    lower: Bound | None
    upper: Bound | None


@dataclass(frozen=True)
class FixedRange:
    lower: Bound | None
    upper: Bound | None


type VerticalRange = MinimalRange | FixedRange


@dataclass(frozen=True, kw_only=True)
class Curve:
    quantity: Quantity
    attributes: CurveAttributes


@dataclass(frozen=True)
class Stack:
    members: Sequence[Curve]
    inverse: bool
    reference: Curve | None = None


@dataclass(frozen=True)
class Line:
    curve: Curve
    inverse: bool


@dataclass(frozen=True)
class Rule:
    curve: Curve
    inverse: bool


@dataclass(frozen=True, kw_only=True)
class Graph:
    name: str
    title: str
    graph_type: str
    vertical_range: VerticalRange | None = None
    stacks: Sequence[Stack] = ()
    lines: Sequence[Line] = ()
    rules: Sequence[Rule] = ()

    def rrd_metrics(self) -> Sequence[RRDMetric]:
        return list(
            dict.fromkeys(
                rrd_metric
                for quantity in itertools.chain(
                    (m.quantity for g in self.stacks for m in g.members),
                    (g.reference.quantity for g in self.stacks if g.reference is not None),
                    (line.curve.quantity for line in self.lines),
                    (rule.curve.quantity for rule in self.rules),
                )
                for rrd_metric in quantity.rrd_metrics()
            )
        )
