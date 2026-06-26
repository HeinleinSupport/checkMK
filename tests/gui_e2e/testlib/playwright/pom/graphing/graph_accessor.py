#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

"""One consistent way to reach a graph regardless of which surface hosts it.

Resolves the container scoping a graph, absorbing surface-specific concerns
(dashboard-widget scoping, designer-preview container, iframe boundaries). The
selector for the rendered graph component itself (`graph_root`) is a skeleton
until the new engine renders on a surface.
"""

import logging

from playwright.sync_api import Locator

from tests.gui_e2e.testlib.playwright.pom.graphing.graph_surfaces import GraphContainment
from tests.gui_e2e.testlib.playwright.pom.page import CmkPage

logger = logging.getLogger(__name__)

# Container of the current (legacy) graph rendering; swapped for the new
# engine's container once the component lands. Uses the always-present
# ``div.graph`` rather than the ``div.graph_with_timeranges`` wrapper, which is
# absent on the forecast and dashboard-widget surfaces (show_time_range_previews
# defaults to False there).
_GRAPH_CONTAINER_SELECTOR = "div.graph:not(.preview)"
_DESIGNER_PREVIEW_SELECTOR = "#graph_0"


class GraphAccessor:
    """Resolve the container that hosts a graph, hiding surface differences.

    Reuses ``owner.main_area`` so the existing mixed-version iframe handling applies.
    """

    def __init__(self, owner: CmkPage) -> None:
        self._owner = owner
        self.page = owner.page

    def container(
        self,
        containment: GraphContainment,
        *,
        widget: Locator | None = None,
        iframed: bool = False,
    ) -> Locator:
        """Return the locator scoping the graph for the given containment context.

        ``widget`` is required for `DASHBOARD_WIDGET` (from e.g.
        ``BaseDashboard.get_widget``); ``iframed`` descends through the widget's iframe.
        """
        match containment:
            case GraphContainment.PAGE_DIRECT:
                return self._owner.main_area.locator(_GRAPH_CONTAINER_SELECTOR)
            case GraphContainment.DESIGNER_PREVIEW:
                return self._owner.main_area.locator(_DESIGNER_PREVIEW_SELECTOR)
            case GraphContainment.DASHBOARD_WIDGET:
                if widget is None:
                    raise ValueError(
                        "A widget locator is required for DASHBOARD_WIDGET containment."
                    )
                if iframed:
                    return widget.frame_locator("iframe").locator(_GRAPH_CONTAINER_SELECTOR)
                return widget.locator(_GRAPH_CONTAINER_SELECTOR)
            case _:
                raise ValueError(f"Unknown graph containment: {containment!r}")

    def graph_root(self, containment: GraphContainment, **kwargs: object) -> Locator:
        """Return the rendered graph component within its container.

        Skeleton: descend from `container(...)` into the component root once the
        new graph engine exposes a stable selector/hook.
        """
        raise NotImplementedError(
            "graph_root is scaffolding: complete once the graph component "
            "exposes its selector/hook contract."
        )
