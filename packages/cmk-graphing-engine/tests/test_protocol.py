#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

"""The open quantity protocol: a custom quantity kind defined entirely outside the engine
is evaluated by the engine without any change to its code."""

from collections.abc import Iterable
from dataclasses import dataclass

from cmk.graphing_engine import (
    AutoPrecision,
    Curve,
    CurveAttributes,
    DecimalNotation,
    EvaluatedCurve,
    EvaluatedQuantity,
    Graph,
    HostName,
    Line,
    MetricName,
    RRDMetric,
    Service,
    ServiceName,
    TimeRange,
    TimeSeries,
    Unit,
)
from cmk.graphing_engine._evaluate import evaluate_graph
from cmk.graphing_engine._perfdata import PerformanceData
from cmk.graphing_engine._quantities import EvaluationContext, Quantity

_UNIT = Unit(notation=DecimalNotation(""), precision=AutoPrecision(2))
_TR = TimeRange(start=0, end=30, step=10)  # three data points


def _metric(name: str) -> RRDMetric:
    return RRDMetric(
        host_name=HostName("h"), service_name=ServiceName("svc"), metric_name=MetricName(name)
    )


def _data(*, value: float | None) -> PerformanceData:
    return PerformanceData(value=value, originals=[])


@dataclass(frozen=True)
class Negated:
    """A custom quantity, unknown to the engine, that flips the sign of another quantity."""

    operand: Quantity

    def ident(self) -> str:
        return f"negated({self.operand.ident()})"

    def rrd_metrics(self) -> Iterable[RRDMetric]:
        yield from self.operand.rrd_metrics()

    def evaluate(self, context: EvaluationContext) -> EvaluatedQuantity | None:
        evaluated = self.operand.evaluate(context)
        if evaluated is None:
            return None
        return EvaluatedQuantity(
            value=None if evaluated.value is None else -evaluated.value,
            time_series=TimeSeries(
                time_range=context.time_range,
                values=[None if v is None else -v for v in evaluated.time_series.values],
            ),
        )


def test_custom_quantity_is_accepted_as_a_quantity() -> None:
    # Static structural conformance: a Negated is usable wherever a Quantity is expected.
    a = _metric("a")
    quantity: Quantity = Negated(operand=a)
    assert list(quantity.rrd_metrics()) == [a]


def test_engine_evaluates_a_custom_quantity_without_engine_changes() -> None:
    a = _metric("a")
    attributes = CurveAttributes(title="neg a", unit=_UNIT, color="#000000")
    graph = Graph(
        name="g",
        title="g",
        graph_type="test",
        lines=[
            Line(curve=Curve(quantity=Negated(operand=a), attributes=attributes), inverse=False)
        ],
    )
    result = evaluate_graph(
        graph,
        {
            Service(host_name=HostName("h"), service_name=ServiceName("svc")): {
                MetricName("a"): _data(value=3.0)
            }
        },
        {a: TimeSeries(time_range=_TR, values=[1.0, None, 3.0])},
        _TR,
    )
    assert result.lines[0].curve == EvaluatedCurve(
        id="negated(metric:h/svc/a)",
        attributes=attributes,
        value=-3.0,
        time_series=TimeSeries(time_range=_TR, values=[-1.0, None, -3.0]),
    )
