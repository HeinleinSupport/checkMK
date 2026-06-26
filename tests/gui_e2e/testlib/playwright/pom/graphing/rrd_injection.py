#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

"""Create RRD files with controlled data shapes (varying, gaps) for graph tests.

Written on the site by `_rrd_injection_helper.py`. Visibility caveat: the engine
reads RRD via the livestatus ``rrddata:`` column, so only the RRD of a *monitored*
service surfaces — write to that service's real path with its ``.info`` sidecar
(e.g. overwrite an already-discovered service's RRD). The helper writes a single
``DS:value``, but the core names per-service DSes numerically (``1``, ``2``, …) and
maps them to metric names in the ``.info`` sidecar; overwriting a discovered
``.rrd`` while leaving its ``.info`` in place makes the engine miss the DS and read
empty, so the injected DS name must match the existing ``.info`` (or the ``.info``
must be regenerated). Binding to a concrete service is left to the suite.
"""

import logging
import time
from dataclasses import dataclass
from enum import StrEnum
from typing import Final

from cmk.utils.misc import pnp_cleanup
from tests.testlib.site import Site

logger = logging.getLogger(__name__)

# Default RRD geometry: one sample per minute over roughly a day.
_DEFAULT_STEP_SECONDS: Final = 60
_DEFAULT_SAMPLE_COUNT: Final = 1440

# Europe/Berlin DST transition instants. Pass as inject_rrd(start=...) with the
# user timezone set to a DST zone; the test selects the historical window so the
# rendered axis crosses the transition.
#
# Fall-back is the relevant one for the "no duplicate X-axis labels" regression
# (Werk #14830): clocks go back, so local 02:00-02:59 occurs *twice* and a naive
# axis would emit the same label twice. Spring-forward merely *skips* the hour
# (no duplicate), so it does not exercise that regression.
DST_FALL_BACK_BERLIN_UTC: Final = 1729990800  # 2024-10-27 01:00 UTC; local 03:00->02:00
DST_SPRING_FORWARD_BERLIN_UTC: Final = 1711846800  # 2024-03-31 01:00 UTC; local 02:00->03:00


class GraphDataShape(StrEnum):
    """The controlled data shapes a graph test fixture can request."""

    VARYING = "varying"
    GAPS = "gaps"


def service_rrd_path(host_name: str, service_description: str) -> str:
    """RRD path relative to ``OMD_ROOT`` the core reads for a service's metrics.

    Applies the core's `pnp_cleanup` quoting to both path elements
    (e.g. "CPU load" -> "CPU_load.rrd").
    """
    return f"var/check_mk/rrd/{pnp_cleanup(host_name)}/{pnp_cleanup(service_description)}.rrd"


@dataclass(frozen=True)
class InjectedRrd:
    """An RRD file created on the site for a graph test."""

    rel_path: str
    shape: GraphDataShape
    step: int
    start: int
    count: int


def inject_rrd(
    site: Site,
    shape: GraphDataShape,
    *,
    host_name: str,
    service_description: str,
    step: int = _DEFAULT_STEP_SECONDS,
    start: int | None = None,
    count: int = _DEFAULT_SAMPLE_COUNT,
) -> InjectedRrd:
    """Write the data shape to a service's RRD at the path the core reads.

    Writes to `service_rrd_path` (the core's `pnp_cleanup`-quoted per-service
    path); the service must be monitored with a matching ``.info`` (see module
    docstring). ``start`` defaults to now (the test host's clock) minus the window
    length so data lands in default relative views; pass an explicit ``start``
    (e.g. `DST_FALL_BACK_BERLIN_UTC`) for a historical window.
    """
    if start is None:
        start = int(time.time()) - count * step
    rel_path = service_rrd_path(host_name, service_description)
    logger.info("Injecting RRD '%s' with shape '%s'", rel_path, shape.value)
    site.python_helper("_rrd_injection_helper.py").check_output(
        args=[shape.value, rel_path, str(step), str(start), str(count)]
    )
    return InjectedRrd(rel_path=rel_path, shape=shape, step=step, start=start, count=count)
