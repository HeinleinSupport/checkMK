#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

"""Graph discovery / data via the REST API. Skipped skeletons (CMK-35973).

D-01/D-02 (R1.1 Area 1) and E-05 (R1.4 Area 3, folded from the struck R1.1 E-01).
Complete once the discovery/data REST endpoints exist.
"""

import pytest

from tests.testlib.graphing import SKIP_PENDING_GRAPH_BACKEND
from tests.testlib.site import Site


@pytest.mark.skip(reason=SKIP_PENDING_GRAPH_BACKEND)
def test_graph_discovery_returns_empty_for_service_without_perfdata(site: Site) -> None:
    """D-01 (R1.1 Area 1): a perfdata-less service yields an empty graph set, not an error.

    Do: create a host whose only service has no perfdata; call graph-discovery for it.
    Assert: empty list, not 4xx/5xx.
    """
    pytest.fail("CMK-35973 skeleton: body not implemented")


@pytest.mark.skip(reason=SKIP_PENDING_GRAPH_BACKEND)
def test_graph_discovery_unknown_graph_id_is_not_a_server_error(site: Site) -> None:
    """D-02 (R1.1 Area 1): an unknown graph id degrades gracefully.

    Do: create and discover a host; call graph-discovery with a non-existent graph_id.
    Assert: empty list or 404, not a server error.
    """
    pytest.fail("CMK-35973 skeleton: body not implemented")


@pytest.mark.skip(reason=SKIP_PENDING_GRAPH_BACKEND)
def test_graph_data_for_missing_rrd_returns_empty_not_error(site: Site) -> None:
    """E-05 (R1.4 Area 3): graph data for a never-checked service is empty, not a 500.

    Do: create and discover a host but let no check run (no RRD yet); call graph-data.
    Assert: HTTP 200 with an empty/all-null series; no traceback.
    """
    pytest.fail("CMK-35973 skeleton: body not implemented")
