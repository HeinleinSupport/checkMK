#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from __future__ import annotations

import enum
import math
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, KW_ONLY
from typing import Protocol

from ._options import ConsolidationFunction, TimeRange
from ._perfdata import HostName, MetricName, PerformanceData, Service, ServiceName, TimeSeries
from ._units import CurveAttributes


@dataclass(frozen=True, kw_only=True)
class EvaluationContext:
    performance_data: Mapping[Service, Mapping[MetricName, PerformanceData]]
    time_series: Mapping[RRDMetric, TimeSeries]
    time_range: TimeRange

    def data_of(self, metric: RRDMetric) -> PerformanceData | None:
        service = Service(host_name=metric.host_name, service_name=metric.service_name)
        return self.performance_data.get(service, {}).get(metric.metric_name)


@dataclass(frozen=True, kw_only=True)
class EvaluatedQuantity:
    value: float | None
    time_series: TimeSeries


class Quantity(Protocol):
    def ident(self) -> str: ...

    def rrd_metrics(self) -> Iterable[RRDMetric]: ...

    def evaluate(self, context: EvaluationContext) -> EvaluatedQuantity | None: ...


type _Operator = Callable[[Sequence[float | None]], float | None]


def _op_sum(point: Sequence[float | None]) -> float | None:
    return sum(value for value in point if value is not None)


def _op_product(point: Sequence[float | None]) -> float | None:
    if None in point:
        return None
    return math.prod(value for value in point if value is not None)


def _op_difference(point: Sequence[float | None]) -> float | None:
    minuend, subtrahend = point
    if minuend is None or subtrahend is None:
        return None
    return minuend - subtrahend


def _op_fraction(point: Sequence[float | None]) -> float | None:
    dividend, divisor = point
    if dividend is None or divisor is None or divisor == 0:
        return None
    return dividend / divisor


def _apply(operator: _Operator, point: Sequence[float | None]) -> float | None:
    if all(value is None for value in point):
        return None
    return operator(point)


def _num_points(time_range: TimeRange) -> int:
    if time_range.step <= 0:
        return 0
    return max(0, (time_range.end - time_range.start) // time_range.step)


def _constant_time_series(value: float | None, time_range: TimeRange) -> TimeSeries:
    return TimeSeries(time_range=time_range, values=[value] * _num_points(time_range))


def _apply_operator(
    operator: _Operator,
    operands: Sequence[EvaluatedQuantity | None],
    context: EvaluationContext,
) -> EvaluatedQuantity:
    values = [None if operand is None else operand.value for operand in operands]
    time_series = [
        _constant_time_series(None, context.time_range) if operand is None else operand.time_series
        for operand in operands
    ]
    return EvaluatedQuantity(
        value=None if any(value is None for value in values) else operator(values),
        time_series=TimeSeries(
            time_range=context.time_range,
            values=[_apply(operator, point) for point in zip(*(ts.values for ts in time_series))],
        ),
    )


@dataclass(frozen=True)
class Constant:
    value: int | float
    display: CurveAttributes | None = None

    def ident(self) -> str:
        return f"constant:{self.value}"

    def rrd_metrics(self) -> Iterable[RRDMetric]:
        return ()

    def evaluate(self, context: EvaluationContext) -> EvaluatedQuantity:
        return EvaluatedQuantity(
            value=self.value, time_series=_constant_time_series(self.value, context.time_range)
        )


@dataclass(frozen=True, kw_only=True)
class RRDMetric:
    host_name: HostName
    service_name: ServiceName
    metric_name: MetricName
    consolidation_function: ConsolidationFunction | None = None

    def ident(self) -> str:
        return f"metric:{self.host_name}/{self.service_name}/{self.metric_name}"

    def rrd_metrics(self) -> Iterable[RRDMetric]:
        yield self

    def evaluate(self, context: EvaluationContext) -> EvaluatedQuantity | None:
        data = context.data_of(self)
        existing = context.time_series.get(self)
        if not ((data is not None and data.value is not None) or existing is not None):
            return None
        return EvaluatedQuantity(
            value=None if data is None else data.value,
            time_series=(
                existing
                if existing is not None
                else _constant_time_series(None, context.time_range)
            ),
        )


class ScalarType(enum.StrEnum):
    WARNING = "warning"
    CRITICAL = "critical"
    LOWER_WARNING = "lower_warning"
    LOWER_CRITICAL = "lower_critical"
    MINIMUM = "minimum"
    MAXIMUM = "maximum"


_SCALAR_VALUE: Mapping[ScalarType, Callable[[PerformanceData], float | None]] = {
    ScalarType.WARNING: lambda data: data.warning,
    ScalarType.CRITICAL: lambda data: data.critical,
    ScalarType.LOWER_WARNING: lambda data: data.lower_warning,
    ScalarType.LOWER_CRITICAL: lambda data: data.lower_critical,
    ScalarType.MINIMUM: lambda data: data.minimum,
    ScalarType.MAXIMUM: lambda data: data.maximum,
}


@dataclass(frozen=True)
class ScalarOf:
    metric: RRDMetric
    scalar_type: ScalarType
    color: str | None = None

    def ident(self) -> str:
        return f"{self.scalar_type}:{self.metric.ident()}"

    def rrd_metrics(self) -> Iterable[RRDMetric]:
        yield self.metric

    def evaluate(self, context: EvaluationContext) -> EvaluatedQuantity | None:
        if (data := context.data_of(self.metric)) is None:
            return None
        value = _SCALAR_VALUE[self.scalar_type](data)
        return EvaluatedQuantity(
            value=value, time_series=_constant_time_series(value, context.time_range)
        )


@dataclass(frozen=True)
class Sum:
    summands: Sequence[Quantity]
    display: CurveAttributes | None = None

    def ident(self) -> str:
        return f"sum({','.join(summand.ident() for summand in self.summands)})"

    def rrd_metrics(self) -> Iterable[RRDMetric]:
        for summand in self.summands:
            yield from summand.rrd_metrics()

    def evaluate(self, context: EvaluationContext) -> EvaluatedQuantity | None:
        evaluated = [summand.evaluate(context) for summand in self.summands]
        if not evaluated or evaluated[0] is None:
            return None
        return _apply_operator(_op_sum, evaluated, context)


@dataclass(frozen=True)
class Product:
    factors: Sequence[Quantity]
    display: CurveAttributes | None = None

    def ident(self) -> str:
        return f"product({','.join(factor.ident() for factor in self.factors)})"

    def rrd_metrics(self) -> Iterable[RRDMetric]:
        for factor in self.factors:
            yield from factor.rrd_metrics()

    def evaluate(self, context: EvaluationContext) -> EvaluatedQuantity:
        return _apply_operator(
            _op_product, [factor.evaluate(context) for factor in self.factors], context
        )


@dataclass(frozen=True)
class Difference:
    _: KW_ONLY
    minuend: Quantity
    subtrahend: Quantity
    display: CurveAttributes | None = None

    def ident(self) -> str:
        return f"difference({self.minuend.ident()},{self.subtrahend.ident()})"

    def rrd_metrics(self) -> Iterable[RRDMetric]:
        yield from self.minuend.rrd_metrics()
        yield from self.subtrahend.rrd_metrics()

    def evaluate(self, context: EvaluationContext) -> EvaluatedQuantity | None:
        minuend = self.minuend.evaluate(context)
        if minuend is None:
            return None
        return _apply_operator(
            _op_difference, [minuend, self.subtrahend.evaluate(context)], context
        )


@dataclass(frozen=True)
class Fraction:
    _: KW_ONLY
    dividend: Quantity
    divisor: Quantity
    display: CurveAttributes | None = None

    def ident(self) -> str:
        return f"fraction({self.dividend.ident()},{self.divisor.ident()})"

    def rrd_metrics(self) -> Iterable[RRDMetric]:
        yield from self.dividend.rrd_metrics()
        yield from self.divisor.rrd_metrics()

    def evaluate(self, context: EvaluationContext) -> EvaluatedQuantity:
        return _apply_operator(
            _op_fraction, [self.dividend.evaluate(context), self.divisor.evaluate(context)], context
        )
