#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

"""Skeletons for the common graph-interaction needs shared by the graph test suites.

Scaffolding only: the new engine renders on no page yet, so the bodies raise
`NotImplementedError`. The data-request endpoint is intentionally not listed -
the engine's update path goes through its own data-update dispatcher (module path
to be confirmed once the engine is wired to a page); resolve it against the actual
engine module when completing the control/fail methods.
"""

from playwright.sync_api import Page

_TODO = "Scaffolding; complete once the new engine renders on a surface."


class GraphInteractions:
    """Common graph interactions, scaffolded for completion once the graph exists."""

    def __init__(self, page: Page) -> None:
        self.page = page

    def control_graph_data_request(self) -> None:
        """Route the engine's data-update endpoint to hold/rewrite it (loading state)."""
        raise NotImplementedError(_TODO)

    def fail_graph_data_request(self) -> None:
        """Route the engine's data-update endpoint to abort/500 it (error state)."""
        raise NotImplementedError(_TODO)

    def assert_old_engine_unused(self) -> None:
        """Assert the legacy ``div.graph_with_timeranges`` canvas is absent and the
        new graph component rendered instead."""
        raise NotImplementedError(_TODO)

    def inspect_rendered_output(self) -> None:
        """Read the rendered graph for assertions.

        The graph is a two-layer composite: axes/grid/labels are SVG and the
        legend is DOM (both assertable via locators); the data curves are drawn
        to a canvas, so assert those via screenshot/pixel comparison or exposed
        component state, not DOM queries.
        """
        raise NotImplementedError(_TODO)
