#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

import re
from collections.abc import Mapping, Sequence

from ._objects import (
    MetricName,
    MetricTranslation,
    PerformanceData,
    RawMetricNames,
    RawPerformanceData,
    RawPerformanceValue,
    RRDOriginal,
)

_PREDICT_PREFIXES = ("predict_lower_", "predict_")


def _split_predict_prefix(metric_name: str) -> tuple[str, str]:
    for prefix in _PREDICT_PREFIXES:
        if metric_name.startswith(prefix):
            return prefix, metric_name[len(prefix) :]
    return "", metric_name


def _translations_for_command(
    check_command: str,
    translations: Mapping[str, Mapping[MetricName, MetricTranslation]],
) -> Mapping[MetricName, MetricTranslation]:
    if not check_command:
        return {}
    if check_command in translations:
        return translations[check_command]
    if check_command.startswith("check_mk-mgmt_"):
        return translations.get(check_command.replace("check_mk-mgmt_", "check_mk-", 1), {})
    return {}


def _find_translation(
    metric_name: MetricName,
    translations: Mapping[MetricName, MetricTranslation],
) -> MetricTranslation:
    if (translation := translations.get(metric_name)) is not None:
        return translation
    for pattern, translation in translations.items():
        if pattern.startswith("~") and re.compile(pattern[1:]).match(metric_name):
            return translation
    return MetricTranslation(name=metric_name)


def _reverse_translations(
    canonical_name: MetricName,
    translations: Mapping[MetricName, MetricTranslation],
) -> Mapping[MetricName, float]:
    return {
        old_name: translation.scale
        for old_name, translation in translations.items()
        if not old_name.startswith("~") and translation.name == canonical_name
    }


def originals_for_metric_name(
    metric_name: MetricName,
    translations: Mapping[str, Mapping[MetricName, MetricTranslation]],
    check_command: str,
) -> Sequence[RRDOriginal]:
    command_translations = _translations_for_command(check_command, translations)
    prefix, bare_name = _split_predict_prefix(metric_name)
    seen = {metric_name}
    originals = [RRDOriginal(metric_name=metric_name, scale=1.0)]
    for old_name, scale in _reverse_translations(
        MetricName(bare_name), command_translations
    ).items():
        if (column := MetricName(f"{prefix}{old_name}")) not in seen:
            originals.append(RRDOriginal(metric_name=column, scale=scale))
            seen.add(column)
    return originals


def translate_metric_names(
    raw_metrics: RawMetricNames,
    translations: Mapping[str, Mapping[MetricName, MetricTranslation]],
) -> frozenset[MetricName]:
    command_translations = _translations_for_command(raw_metrics.check_command, translations)
    names = set()
    for metric_name in raw_metrics.metric_names:
        prefix, bare_name = _split_predict_prefix(metric_name)
        translation = _find_translation(MetricName(bare_name), command_translations)
        names.add(MetricName(f"{prefix}{translation.name}"))
    return frozenset(names)


def translate_performance_data(
    raw_performance_data: RawPerformanceData,
    translations: Mapping[str, Mapping[MetricName, MetricTranslation]],
) -> Mapping[MetricName, PerformanceData]:
    command_translations = _translations_for_command(
        raw_performance_data.check_command, translations
    )
    originals_by_name: dict[MetricName, list[RRDOriginal]] = {}
    raw_value_by_name: dict[MetricName, tuple[RawPerformanceValue, float]] = {}
    for raw_perf_value in raw_performance_data.values:
        prefix, bare_name = _split_predict_prefix(raw_perf_value.metric_name)
        translation = _find_translation(MetricName(bare_name), command_translations)
        name = MetricName(f"{prefix}{translation.name}")
        originals_by_name.setdefault(name, []).append(
            RRDOriginal(metric_name=raw_perf_value.metric_name, scale=translation.scale)
        )
        raw_value_by_name[name] = (raw_perf_value, translation.scale)

    result: dict[MetricName, PerformanceData] = {}
    for name, (raw_perf_value, scale) in raw_value_by_name.items():
        prefix, bare_name = _split_predict_prefix(name)
        present = {original.metric_name for original in originals_by_name[name]}
        deprecated = [
            RRDOriginal(metric_name=old_column, scale=old_scale)
            for old_name, old_scale in _reverse_translations(
                MetricName(bare_name), command_translations
            ).items()
            if (old_column := MetricName(f"{prefix}{old_name}")) not in present
        ]

        def _scaled(value: float | None, scale: float = scale) -> float | None:
            return None if value is None else value * scale

        result[name] = PerformanceData(
            value=_scaled(raw_perf_value.value),
            originals=[*originals_by_name[name], *deprecated],
            lower_warning=_scaled(raw_perf_value.lower_warning),
            lower_critical=_scaled(raw_perf_value.lower_critical),
            warning=_scaled(raw_perf_value.warning),
            critical=_scaled(raw_perf_value.critical),
            minimum=_scaled(raw_perf_value.minimum),
            maximum=_scaled(raw_perf_value.maximum),
        )
    return result
