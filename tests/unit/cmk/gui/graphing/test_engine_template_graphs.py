#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field

import pytest

from cmk.ccc.exceptions import MKGeneralException
from cmk.graphing.v1 import graphs as graphs_v1
from cmk.graphing.v1 import metrics as metrics_v1
from cmk.graphing.v1 import Title
from cmk.graphing_engine import (
    ConsolidationFunction,
    HostName,
    MetricName,
    RawMetricNames,
    RawPerformanceData,
    RawPerformanceValue,
    RRDMetric,
    ScalarOf,
    ScalarType,
    Service,
    ServiceName,
    TimeRange,
    TimeSeries,
)
from cmk.gui.graphing._engine_template_graphs import (
    build_template_graphs,
    evaluate_template_graphs,
)

_SERVICE = Service(host_name=HostName("h"), service_name=ServiceName("svc"))
_METRIC = "x"
_DISCOVERY_RANGE = TimeRange(start=0, end=60, step=10)


@dataclass
class _FakeRRDFetchRawMetricNames:
    metric_names: Sequence[str] = (_METRIC,)

    def __call__(self, services: Sequence[Service]) -> Mapping[Service, RawMetricNames]:
        return {
            service: RawMetricNames(
                check_command="check_mk-foo",
                metric_names=[MetricName(name) for name in self.metric_names],
            )
            for service in services
        }


@dataclass
class _FakeRRDDataSource:
    values: Mapping[str, RawPerformanceValue] = field(
        default_factory=lambda: {_METRIC: RawPerformanceValue(value=1.0)}
    )
    requested_ranges: list[TimeRange] = field(default_factory=list)

    def _data(self, services: Iterable[Service]) -> Mapping[Service, RawPerformanceData]:
        return {
            service: RawPerformanceData(
                check_command="check_mk-foo",
                values={MetricName(name): value for name, value in self.values.items()},
            )
            for service in services
        }

    def fetch_raw_performance_data(
        self, rrd_metrics: Sequence[RRDMetric]
    ) -> Mapping[Service, RawPerformanceData]:
        return self._data(
            Service(host_name=metric.host_name, service_name=metric.service_name)
            for metric in rrd_metrics
        )

    def fetch_time_series(
        self,
        rrd_metrics: Sequence[RRDMetric],
        *,
        consolidation_function: ConsolidationFunction,
        time_range: TimeRange,
    ) -> Mapping[RRDMetric, TimeSeries]:
        self.requested_ranges.append(time_range)
        return {
            metric: TimeSeries(time_range=time_range, values=[1.0, 1.0, 1.0])
            for metric in rrd_metrics
        }


def test_template_lifecycle_discover_and_update() -> None:
    # Discovery builds the display-resolved graphs (every curve carries its attributes, but no data and no
    # render parameters); the per-type update evaluates them over freshly fetched data for the range it is
    # given. The unclaimed metric becomes a fallback single-metric graph that carries the four threshold
    # rules the engine builds itself.
    rrd = _FakeRRDDataSource()
    graphs = build_template_graphs(
        service=_SERVICE,
        registered_graphs=[],
        registered_metrics={},
        registered_translations=[],
        fetch_raw_metric_names=_FakeRRDFetchRawMetricNames(),
    )
    [fallback] = [graph for graph in graphs if graph.name == _METRIC]
    assert [
        rule.curve.quantity.scalar_type
        for rule in fallback.rules
        if isinstance(rule.curve.quantity, ScalarOf)
    ] == [
        ScalarType.WARNING,
        ScalarType.CRITICAL,
        ScalarType.LOWER_WARNING,
        ScalarType.LOWER_CRITICAL,
    ]
    # Discovery fetches performance data only, never the time series.
    assert rrd.requested_ranges == []

    evaluated = evaluate_template_graphs(
        graphs=graphs,
        consolidation_function=ConsolidationFunction.MAX,
        time_range=_DISCOVERY_RANGE,
        registered_translations=[],
        rrd=rrd,
    )

    assert len(evaluated) == len(graphs)
    # The update fetches the series for the range it is given.
    assert rrd.requested_ranges
    assert all(time_range == _DISCOVERY_RANGE for time_range in rrd.requested_ranges)

    # A template graph has a single value axis, so a plugin drawing curves of different units cannot
    # share it — discovery rejects it (legacy parity).
    with pytest.raises(MKGeneralException, match="different units"):
        build_template_graphs(
            service=_SERVICE,
            registered_graphs=[
                graphs_v1.Graph(
                    name="mixed",
                    title=Title("Mixed"),
                    simple_lines=["bytes_metric", "seconds_metric"],
                )
            ],
            registered_metrics={
                "bytes_metric": metrics_v1.Metric(
                    name="bytes_metric",
                    title=Title("Bytes"),
                    unit=metrics_v1.Unit(metrics_v1.DecimalNotation("B")),
                    color=metrics_v1.Color.BLUE,
                ),
                "seconds_metric": metrics_v1.Metric(
                    name="seconds_metric",
                    title=Title("Seconds"),
                    unit=metrics_v1.Unit(metrics_v1.DecimalNotation("s")),
                    color=metrics_v1.Color.GREEN,
                ),
            },
            registered_translations=[],
            fetch_raw_metric_names=_FakeRRDFetchRawMetricNames(("bytes_metric", "seconds_metric")),
        )
