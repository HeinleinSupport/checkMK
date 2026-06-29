#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

"""Shared skip reasons for the graphing (IGU) test skeletons (CMK-35973).

The reason names a skeleton's dependency, which also sets the enablement order (grep a
constant to find every skeleton blocked on the same dependency):

- ``SKIP_PENDING_GRAPH_BACKEND`` - integration/composition tests needing only the backend
  (discovery/data REST + ``<cmk-graph>`` embedding); enablable first.
- ``SKIP_PENDING_GRAPH_ENGINE`` - GUI E2E tests needing the engine to render on a surface.
"""

from typing import Final

SKIP_PENDING_GRAPH_BACKEND: Final = (
    "CMK-35973 skeleton: pending the graph backend (discovery/data REST + "
    "<cmk-graph> embedding); enable once the backend lands."
)
SKIP_PENDING_GRAPH_ENGINE: Final = (
    "CMK-35973 skeleton: pending the new graph engine rendering on this surface."
)
