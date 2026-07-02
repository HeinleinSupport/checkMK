#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from collections.abc import Iterable, Mapping, Sequence
from typing import Protocol

from cmk.graphing.v1 import translations as translations_v1

from ._evaluate import evaluate_graph, EvaluatedGraph
from ._from_api import parse_translations_from_api
from ._objects import (
    Graph,
    MetricName,
    PerformanceData,
    RawMetricNames,
    RawPerformanceData,
    RRDMetric,
    Service,
    TimeSeries,
)
from ._options import ConsolidationFunction, TimeRange
from ._resample import resample
from ._translate import (
    originals_for_metric_name,
    translate_metric_names,
    translate_performance_data,
)


class RRDSource(Protocol):
    def fetch_available_metric_names(
        self, services: Sequence[Service]
    ) -> Mapping[Service, RawMetricNames]: ...

    def fetch_performance_data(
        self, rrd_metrics: Sequence[RRDMetric]
    ) -> Mapping[Service, RawPerformanceData]: ...

    def fetch_time_series(
        self,
        rrd_metrics: Sequence[RRDMetric],
        *,
        consolidation_function: ConsolidationFunction,
        time_range: TimeRange,
    ) -> Mapping[RRDMetric, TimeSeries]: ...


def _consolidation_function(
    metric: RRDMetric, consolidation_function: ConsolidationFunction
) -> ConsolidationFunction:
    return (
        consolidation_function
        if metric.consolidation_function is None
        else metric.consolidation_function
    )


def _scaled(time_series: TimeSeries, scale: float) -> TimeSeries:
    if scale == 1.0:
        return time_series
    return TimeSeries(
        time_range=time_series.time_range,
        values=[None if value is None else value * scale for value in time_series.values],
    )


def _merge(series: Sequence[TimeSeries], time_range: TimeRange) -> TimeSeries:
    return TimeSeries(
        time_range=time_range,
        values=[
            next((value for value in point if value is not None), None)
            for point in zip(*(member.values for member in series))
        ],
    )


def _fetch_time_series(
    *,
    graph: Graph,
    performance_data: Mapping[Service, Mapping[MetricName, PerformanceData]],
    consolidation_function: ConsolidationFunction,
    time_range: TimeRange,
    rrd: RRDSource,
) -> Mapping[RRDMetric, TimeSeries]:
    rrd_metrics_per_metric: dict[
        RRDMetric, tuple[ConsolidationFunction, list[tuple[RRDMetric, float]]]
    ] = {}
    rrd_metrics_per_function: dict[ConsolidationFunction, list[RRDMetric]] = {}
    for metric in graph.rrd_metrics():
        service = Service(host_name=metric.host_name, service_name=metric.service_name)
        if (data := performance_data.get(service, {}).get(metric.metric_name)) is None:
            continue
        function = _consolidation_function(metric, consolidation_function)
        rrd_metrics = [
            (
                RRDMetric(
                    host_name=metric.host_name,
                    service_name=metric.service_name,
                    metric_name=original.metric_name,
                ),
                original.scale,
            )
            for original in data.originals
        ]
        rrd_metrics_per_metric[metric] = (function, rrd_metrics)
        rrd_metrics_per_function.setdefault(function, []).extend(
            rrd_metric for rrd_metric, _scale in rrd_metrics
        )

    raw_per_function = {
        function: rrd.fetch_time_series(
            list(dict.fromkeys(rrd_metrics)),
            consolidation_function=function,
            time_range=time_range,
        )
        for function, rrd_metrics in rrd_metrics_per_function.items()
    }

    result: dict[RRDMetric, TimeSeries] = {}
    for metric, (function, rrd_metrics) in rrd_metrics_per_metric.items():
        raw = raw_per_function[function]
        scaled = [
            _scaled(resample(raw[rrd_metric], time_range, function), scale)
            for rrd_metric, scale in rrd_metrics
            if rrd_metric in raw
        ]
        if scaled:
            result[metric] = _merge(scaled, time_range)
    return result


def fetch_available_metric_names(
    *,
    services: Iterable[Service],
    translations: Iterable[translations_v1.Translation],
    rrd: RRDSource,
) -> Mapping[Service, frozenset[MetricName]]:
    parsed_translations = parse_translations_from_api(translations)
    available = rrd.fetch_available_metric_names(list(dict.fromkeys(services)))
    return {
        service: translate_metric_names(raw_metrics, parsed_translations)
        for service, raw_metrics in available.items()
    }


def fetch_performance_data(
    *,
    graphs: Sequence[Graph],
    translations: Iterable[translations_v1.Translation],
    rrd: RRDSource,
) -> Mapping[Service, Mapping[MetricName, PerformanceData]]:
    parsed_translations = parse_translations_from_api(translations)
    rrd_metrics = list(dict.fromkeys(metric for graph in graphs for metric in graph.rrd_metrics()))
    raw_performance_data = rrd.fetch_performance_data(rrd_metrics)
    performance_data = {
        service: dict(translate_performance_data(raw, parsed_translations))
        for service, raw in raw_performance_data.items()
    }
    for metric in rrd_metrics:
        service = Service(host_name=metric.host_name, service_name=metric.service_name)
        if (raw := raw_performance_data.get(service)) is None:
            continue
        if metric.metric_name not in performance_data[service]:
            performance_data[service][metric.metric_name] = PerformanceData(
                value=None,
                originals=originals_for_metric_name(
                    metric.metric_name, parsed_translations, raw.check_command
                ),
            )
    return performance_data


def evaluate_graphs(
    *,
    graphs: Sequence[Graph],
    translations: Iterable[translations_v1.Translation],
    consolidation_function: ConsolidationFunction,
    time_range: TimeRange,
    rrd: RRDSource,
) -> Sequence[EvaluatedGraph]:
    performance_data = fetch_performance_data(graphs=graphs, translations=translations, rrd=rrd)
    return [
        evaluate_graph(
            graph,
            performance_data,
            _fetch_time_series(
                graph=graph,
                performance_data=performance_data,
                consolidation_function=consolidation_function,
                time_range=time_range,
                rrd=rrd,
            ),
            time_range,
        )
        for graph in graphs
    ]
