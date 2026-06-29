#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

"""DST timezone regression for the graph X-axis (R1.2 Area 8). Skipped skeleton (CMK-35973).

Uses graph_rrd_dst_boundary (VARYING data at DST_FALL_BACK_BERLIN_UTC, DST-observing tz).
Guards Werk #14830: the fall-back repeats the local hour, which a naive axis labels twice.
"""

import pytest

from tests.gui_e2e.testlib.playwright.pom.graphing.rrd_injection import InjectedRrd
from tests.gui_e2e.testlib.playwright.pom.monitor.dashboard import MainDashboard
from tests.testlib.graphing import SKIP_PENDING_GRAPH_ENGINE


@pytest.mark.skip(reason=SKIP_PENDING_GRAPH_ENGINE)
def test_dst_boundary_has_unique_x_axis_labels(
    dashboard_page: MainDashboard, graph_rrd_dst_boundary: InjectedRrd
) -> None:
    """TZ-01 (R1.2 Area 8): a graph over the DST fall-back has no duplicate X-axis labels.

    Do: with tz Europe/Berlin and RRD data spanning the fall-back, open the graph; collect
    the SVG axis label text.
    Assert: every X-axis label is unique; no uncaught JS error.
    """
    pytest.fail("CMK-35973 skeleton: body not implemented")
