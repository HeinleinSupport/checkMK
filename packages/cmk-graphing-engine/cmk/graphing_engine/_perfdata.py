#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import NewType, Self

from ._options import TimeRange

HostName = NewType("HostName", str)
ServiceName = NewType("ServiceName", str)


class MetricName(str):
    # A metric name normalised to PNP4Nagios format: a str subclass whose construction is a projection
    # (non-injective). The raw name is pnp-cleaned, so a name carrying spaces / ":" / "/" / "\" / NUL is
    # mapped to its canonical RRD identifier.
    def __new__(cls, text: str) -> Self:
        # An embedded null byte is mapped to "_" like the other path-hostile chars: it would otherwise
        # make open() raise "ValueError: embedded null byte" when the RRD is created.
        return super().__new__(
            cls,
            text.replace(" ", "_")
            .replace(":", "_")
            .replace("/", "_")
            .replace("\\", "_")
            .replace("\x00", "_"),
        )


@dataclass(frozen=True, kw_only=True)
class Service:
    host_name: HostName
    service_name: ServiceName


@dataclass(frozen=True, kw_only=True)
class RRDOriginal:
    metric_name: MetricName
    scale: float


@dataclass(frozen=True, kw_only=True)
class PerformanceData:
    value: float | None
    originals: Sequence[RRDOriginal]
    lower_warning: float | None = None
    lower_critical: float | None = None
    warning: float | None = None
    critical: float | None = None
    minimum: float | None = None
    maximum: float | None = None


@dataclass(frozen=True, kw_only=True)
class TimeSeries:
    time_range: TimeRange
    values: Sequence[float | None]


@dataclass(frozen=True, kw_only=True)
class RawPerformanceValue:
    value: float
    warning: float | None = None
    critical: float | None = None
    lower_warning: float | None = None
    lower_critical: float | None = None
    minimum: float | None = None
    maximum: float | None = None


@dataclass(frozen=True, kw_only=True)
class RawPerformanceData:
    check_command: str
    values: Mapping[MetricName, RawPerformanceValue]


@dataclass(frozen=True, kw_only=True)
class RawMetricNames:
    check_command: str
    metric_names: Sequence[MetricName]


@dataclass(frozen=True, kw_only=True)
class MetricTranslation:
    name: MetricName
    scale: float = 1.0
