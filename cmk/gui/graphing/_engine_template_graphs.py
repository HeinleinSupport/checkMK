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
    EngineGraphDispatcher,
    GraphDataRequest,
)
from ._engine_plugins import registered_translations
from ._engine_rrd_source import EngineRRDSource
from ._engine_serialization import (
    consolidation_function_of,
    deserialize_graph,
    engine_quantity_codec,
    ensure_type,
    Json,
    serialize_graph,
    time_range_of,
)
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
    registered_graphs: Sequence[GraphFromAPI],
    registered_metrics: Mapping[str, metrics_v1.Metric],
    registered_translations: Sequence[translations_v1.Translation],
    rrd: RRDSource,
) -> Sequence[Graph]:
    metric_names = fetch_metric_names(
        services=[service],
        translations=registered_translations,
        rrd=rrd,
    ).get(service, frozenset())
    graphs = build_matched_graphs(
        service=service,
        registered_graphs=registered_graphs,
        metrics=registered_metrics,
        localizer=translate_to_current_language,
        metric_names=metric_names,
        graph_type="template",
    )
    for graph in graphs:
        _assert_uniform_unit(graph)
    return graphs


def _serialize_template_graphs(graphs: Sequence[Graph]) -> Json:
    codec = engine_quantity_codec()
    return {"graphs": [serialize_graph(graph, codec) for graph in graphs]}


def _deserialize_template_graphs(data: Mapping[str, object]) -> Sequence[Graph]:
    codec = engine_quantity_codec()
    return [deserialize_graph(graph, codec) for graph in ensure_type(data["graphs"], list)]


def evaluate_template_graphs(
    *,
    graphs: Sequence[Graph],
    consolidation_function: ConsolidationFunction,
    time_range: TimeRange,
    registered_translations: Sequence[translations_v1.Translation],
    rrd: RRDSource,
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
        graphs=_deserialize_template_graphs(request.definition),
        consolidation_function=consolidation_function_of(request.options),
        time_range=time_range_of(request.options),
        registered_translations=registered_translations(),
        rrd=EngineRRDSource(site_id=None, debug=active_config.debug),
    )


TEMPLATE_GRAPH_DISPATCHER = EngineGraphDispatcher(
    graph_type="template",
    serialize=_serialize_template_graphs,
    evaluate=_dispatched_evaluate_template_graphs,
)
