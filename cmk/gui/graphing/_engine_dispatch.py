#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field

from cmk.ccc.plugin_registry import Registry
from cmk.graphing_engine import EvaluatedGraph, Graph

from ._engine_serialization import ensure_type, Json


@dataclass(frozen=True, kw_only=True)
class GraphDataRequest:
    graph_type: str
    definition: Mapping[str, object]
    options: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class EngineGraphDispatcher:
    graph_type: str
    serialize: Callable[[Sequence[Graph]], Json]
    evaluate: Callable[[GraphDataRequest], Sequence[EvaluatedGraph]]


class EngineGraphDispatcherRegistry(Registry[EngineGraphDispatcher]):
    def plugin_name(self, instance: EngineGraphDispatcher) -> str:
        return instance.graph_type


engine_graph_dispatcher_registry = EngineGraphDispatcherRegistry()


def serialize_graphs(graphs: Sequence[Graph]) -> Json:
    by_graph_type: dict[str, list[Graph]] = {}
    for graph in graphs:
        by_graph_type.setdefault(graph.graph_type, []).append(graph)
    serialized: list[object] = []
    for graph_type, batch in by_graph_type.items():
        dispatcher = engine_graph_dispatcher_registry[graph_type]
        serialized.extend(ensure_type(dispatcher.serialize(batch)["graphs"], list))
    return {"graphs": serialized}


def evaluate_graphs(request: GraphDataRequest) -> Sequence[EvaluatedGraph]:
    return engine_graph_dispatcher_registry[request.graph_type].evaluate(request)
