#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

"""
Define repository interfaces for fetching from data sources.

These are intentionally only protocols as they are meant to only signify what sort of domain data
they will return. This allows us to pass stubs when testing our applications.
"""

from collections.abc import Sequence
from typing import Protocol

from ._models import Host, HostFilter, HostSort, RescheduleTarget


class HostRepository(Protocol):
    def fetch(
        self,
        *,
        limit: int,
        query: str,
        sorters: Sequence[HostSort],
        filters: HostFilter,
    ) -> Sequence[Host]:
        """Fetch hosts based on filter criteria."""
        ...

    def count(self, *, query: str, filters: HostFilter) -> int:
        """Count the hosts matching the given criteria."""
        ...

    def reschedule(self, targets: Sequence[RescheduleTarget]) -> None:
        """Force an immediate active check for each target on its site."""
        ...
