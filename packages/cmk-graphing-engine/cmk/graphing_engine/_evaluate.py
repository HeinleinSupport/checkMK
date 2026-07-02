#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

import enum
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import assert_never

from ._objects import (
    Bound,
    Curve,
    CurveAttributes,
    EvaluationContext,
    FixedRange,
    Graph,
    MetricName,
    MinimalRange,
    PerformanceData,
    Quantity,
    RRDMetric,
    Rule,
    Service,
    TimeSeries,
    VerticalRange,
)
from ._options import TimeRange
from ._title import evaluate_title


@dataclass(frozen=True, kw_only=True)
class EvaluatedCurve:
    id: str
    attributes: CurveAttributes
    value: float | None
    time_series: TimeSeries


@dataclass(frozen=True, kw_only=True)
class EvaluatedStack:
    members: Sequence[EvaluatedCurve]
    inverse: bool
    reference: EvaluatedCurve | None = None


@dataclass(frozen=True, kw_only=True)
class EvaluatedLine:
    curve: EvaluatedCurve
    inverse: bool


@dataclass(frozen=True, kw_only=True)
class EvaluatedRule:
    id: str
    attributes: CurveAttributes
    value: float
    inverse: bool


class VerticalRangeType(enum.StrEnum):
    MINIMAL = "minimal"
    FIXED = "fixed"


@dataclass(frozen=True, kw_only=True)
class EvaluatedVerticalRange:
    range_type: VerticalRangeType
    lower: float | None
    upper: float | None


@dataclass(frozen=True, kw_only=True)
class EvaluatedGraph:
    name: str
    title: str
    vertical_range: EvaluatedVerticalRange | None
    stacks: Sequence[EvaluatedStack]
    lines: Sequence[EvaluatedLine]
    rules: Sequence[EvaluatedRule] = ()


def _evaluate_bound(bound: Bound | None, context: EvaluationContext) -> float | None:
    if bound is None:
        return None
    if isinstance(bound, int | float):
        return float(bound)
    evaluated = bound.evaluate(context)
    return None if evaluated is None else evaluated.value


def _evaluate_vertical_range(
    vertical_range: VerticalRange | None,
    context: EvaluationContext,
) -> EvaluatedVerticalRange | None:
    match vertical_range:
        case None:
            return None
        case MinimalRange():
            return EvaluatedVerticalRange(
                range_type=VerticalRangeType.MINIMAL,
                lower=_evaluate_bound(vertical_range.lower, context),
                upper=_evaluate_bound(vertical_range.upper, context),
            )
        case FixedRange():
            return EvaluatedVerticalRange(
                range_type=VerticalRangeType.FIXED,
                lower=_evaluate_bound(vertical_range.lower, context),
                upper=_evaluate_bound(vertical_range.upper, context),
            )
        case _:
            assert_never(vertical_range)


def _drawable_id(quantity: Quantity, *, inverse: bool, seen: Counter[str]) -> str:
    base = ("-" if inverse else "") + quantity.ident()
    seen[base] += 1
    return base if seen[base] == 1 else f"{base}#{seen[base]}"


def _evaluate_curve(
    curve: Curve, curve_id: str, context: EvaluationContext
) -> EvaluatedCurve | None:
    evaluated = curve.quantity.evaluate(context)
    if evaluated is None:
        return None
    return EvaluatedCurve(
        id=curve_id,
        attributes=curve.attributes,
        value=evaluated.value,
        time_series=evaluated.time_series,
    )


def _evaluate_rule(rule: Rule, rule_id: str, context: EvaluationContext) -> EvaluatedRule | None:
    evaluated = rule.curve.quantity.evaluate(context)
    if evaluated is None or evaluated.value is None:
        return None
    return EvaluatedRule(
        id=rule_id,
        attributes=rule.curve.attributes,
        value=evaluated.value,
        inverse=rule.inverse,
    )


def _title_metrics(
    graph: Graph,
    translated_metrics: Mapping[Service, Mapping[MetricName, PerformanceData]],
) -> Mapping[MetricName, PerformanceData]:
    services = {
        Service(host_name=metric.host_name, service_name=metric.service_name)
        for metric in graph.rrd_metrics()
    }
    return {
        name: data
        for service in services
        if service in translated_metrics
        for name, data in translated_metrics[service].items()
    }


def evaluate_graph(
    graph: Graph,
    performance_data: Mapping[Service, Mapping[MetricName, PerformanceData]],
    time_series: Mapping[RRDMetric, TimeSeries],
    time_range: TimeRange,
) -> EvaluatedGraph:
    context = EvaluationContext(
        performance_data=performance_data,
        time_series=time_series,
        time_range=time_range,
    )
    seen: Counter[str] = Counter()
    stacks = []
    for group in graph.stacks:
        members = [
            curve
            for member in group.members
            if (
                curve := _evaluate_curve(
                    member,
                    _drawable_id(member.quantity, inverse=group.inverse, seen=seen),
                    context,
                )
            )
            is not None
        ]
        reference = (
            None
            if group.reference is None
            else _evaluate_curve(
                group.reference,
                _drawable_id(group.reference.quantity, inverse=group.inverse, seen=seen),
                context,
            )
        )
        if members:
            stacks.append(
                EvaluatedStack(members=members, inverse=group.inverse, reference=reference)
            )
    lines = [
        EvaluatedLine(curve=curve, inverse=line.inverse)
        for line in graph.lines
        if (
            curve := _evaluate_curve(
                line.curve,
                _drawable_id(line.curve.quantity, inverse=line.inverse, seen=seen),
                context,
            )
        )
        is not None
    ]
    rules = [
        evaluated
        for rule in graph.rules
        if (
            evaluated := _evaluate_rule(
                rule,
                _drawable_id(rule.curve.quantity, inverse=rule.inverse, seen=seen),
                context,
            )
        )
        is not None
    ]
    return EvaluatedGraph(
        name=graph.name,
        title=evaluate_title(graph.title, _title_metrics(graph, performance_data)),
        vertical_range=_evaluate_vertical_range(graph.vertical_range, context),
        stacks=stacks,
        lines=lines,
        rules=rules,
    )
