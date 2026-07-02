#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field

from cmk.ccc.plugin_registry import Registry
from cmk.graphing_engine import ConsolidationFunction, EvaluatedGraph, TimeRange

from ._engine_serialization import ensure_type


@dataclass(frozen=True, kw_only=True)
class GraphDataRequest:
    graph_type: str
    definition: Mapping[str, object]
    options: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class EngineGraphEvaluator:
    graph_type: str
    evaluate: Callable[[GraphDataRequest], Sequence[EvaluatedGraph]]


class EngineGraphEvaluatorRegistry(Registry[EngineGraphEvaluator]):
    def plugin_name(self, instance: EngineGraphEvaluator) -> str:
        return instance.graph_type


engine_graph_evaluator_registry = EngineGraphEvaluatorRegistry()


def evaluate_graphs(request: GraphDataRequest) -> Sequence[EvaluatedGraph]:
    return engine_graph_evaluator_registry[request.graph_type].evaluate(request)


def consolidation_function_of(request: GraphDataRequest) -> ConsolidationFunction:
    return ensure_type(request.options["consolidation_function"], ConsolidationFunction)


def time_range_of(request: GraphDataRequest) -> TimeRange:
    return ensure_type(request.options["time_range"], TimeRange)
