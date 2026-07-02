#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


from __future__ import annotations

from collections.abc import Mapping, Sequence

from cmk.ccc.exceptions import MKGeneralException
from cmk.graphing.v1 import metrics as metrics_v1
from cmk.graphing.v1 import translations as translations_v1
from cmk.graphing_engine import (
    build_matched_graphs,
    ConsolidationFunction,
    evaluate_graphs,
    EvaluatedGraph,
    fetch_metric_names,
    Graph,
    RRDSource,
    Service,
    TimeRange,
)
from cmk.gui.config import active_config
from cmk.gui.i18n import _, translate_to_current_language

from ._engine_dispatch import (
    consolidation_function_of,
    EngineGraphEvaluator,
    GraphDataRequest,
    time_range_of,
)
from ._engine_plugins import registered_translations
from ._engine_rrd_source import EngineRRDSource
from ._engine_serialization import deserialize_graphs
from ._from_api import GraphFromAPI


def _assert_uniform_unit(graph: Graph) -> None:
    drawn = [
        *(member for stack in graph.stacks for member in stack.members),
        *(stack.reference for stack in graph.stacks if stack.reference is not None),
        *(line.curve for line in graph.lines),
    ]
    units = {curve.attributes.unit for curve in drawn}
    if len(units) > 1:
        raise MKGeneralException(
            _("Cannot create graph with metrics of different units: %s")
            % ", ".join(sorted(repr(unit) for unit in units))
        )


def build_template_graphs(
    *,
    service: Service,
    rrd: RRDSource,
    registered_graphs: Sequence[GraphFromAPI],
    registered_metrics: Mapping[str, metrics_v1.Metric],
    registered_translations: Sequence[translations_v1.Translation],
) -> Sequence[Graph]:
    available = fetch_metric_names(
        services=[service],
        translations=registered_translations,
        rrd=rrd,
    ).get(service, frozenset())
    graphs = build_matched_graphs(
        service=service,
        registered_graphs=registered_graphs,
        metrics=registered_metrics,
        localizer=translate_to_current_language,
        metric_names=available,
        graph_type="template",
    )
    for graph in graphs:
        _assert_uniform_unit(graph)
    return graphs


def evaluate_template_graphs(
    *,
    graphs: Sequence[Graph],
    consolidation_function: ConsolidationFunction,
    time_range: TimeRange,
    rrd: RRDSource,
    registered_translations: Sequence[translations_v1.Translation],
) -> Sequence[EvaluatedGraph]:
    return evaluate_graphs(
        graphs=graphs,
        translations=registered_translations,
        consolidation_function=consolidation_function,
        time_range=time_range,
        rrd=rrd,
    )


def _dispatched_evaluate_template_graphs(request: GraphDataRequest) -> Sequence[EvaluatedGraph]:
    return evaluate_template_graphs(
        graphs=deserialize_graphs(request.definition),
        consolidation_function=consolidation_function_of(request),
        time_range=time_range_of(request),
        rrd=EngineRRDSource(site_id=None, debug=active_config.debug),
        registered_translations=registered_translations(),
    )


TEMPLATE_GRAPH_EVALUATOR = EngineGraphEvaluator(
    graph_type="template", evaluate=_dispatched_evaluate_template_graphs
)
