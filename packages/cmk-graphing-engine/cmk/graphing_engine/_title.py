#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

import json
import re
from collections.abc import Callable, Mapping

from ._perfdata import MetricName, PerformanceData

_TITLE_EXPRESSION_PREFIX = "_EXPRESSION:"
_TITLE_EXPRESSION_PATTERN = re.compile(re.escape(_TITLE_EXPRESSION_PREFIX) + r"\{.*?\}")
_TITLE_SCALARS: Mapping[str, Callable[[PerformanceData], float | None]] = {
    "warn": lambda performance_data: performance_data.warning,
    "crit": lambda performance_data: performance_data.critical,
    "warn_lower": lambda performance_data: performance_data.lower_warning,
    "crit_lower": lambda performance_data: performance_data.lower_critical,
    "min": lambda performance_data: performance_data.minimum,
    "max": lambda performance_data: performance_data.maximum,
}


def _parse_title_expression(raw: str) -> Mapping[str, str]:
    expression: Mapping[str, str] = json.loads(raw[len(_TITLE_EXPRESSION_PREFIX) :])
    return expression


def _evaluate_title_expression(
    raw: str,
    performance_data: Mapping[MetricName, PerformanceData],
) -> float | None:
    expression = _parse_title_expression(raw)
    if (data := performance_data.get(MetricName(expression["metric"]))) is None:
        return None
    if (scalar := _TITLE_SCALARS.get(expression["scalar"])) is None:
        return None
    return scalar(data)


def evaluate_title(
    title: str,
    performance_data: Mapping[MetricName, PerformanceData],
) -> str:
    for raw in _TITLE_EXPRESSION_PATTERN.findall(title):
        value = _evaluate_title_expression(raw, performance_data)
        if value is None:
            return title.split("-", maxsplit=1)[0].strip()
        title = title.replace(raw, str(int(value)), 1)
    return title
