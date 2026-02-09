#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


from collections.abc import Mapping
from typing import Any

from cmk.agent_based.legacy.conversion import (
    # Temporary compatibility layer untile we migrate the corresponding ruleset.
    check_levels_legacy_compatible as check_levels,
)
from cmk.agent_based.v2 import CheckPlugin, CheckResult, DiscoveryResult, Result, Service, State
from cmk.plugins.collection.agent_based.apc_rackpdu_power import Section


def discover_apc_rackpdu_power(section: Section) -> DiscoveryResult:
    yield from (Service(item=item) for item in section)


def check_apc_rackpdu_power(item: str, params: Mapping[str, Any], section: Section) -> CheckResult:
    if (power := section.get(item)) is None:
        return

    if (entry := power.get("current")) is not None:
        value, (state_code, state_text) = entry
        yield from check_levels(
            value,
            "current",
            params=params.get("current"),
            human_readable_func=lambda v: f"{v:.1f} A",
            infoname="Current",
        )
        yield Result(state=State(state_code), summary=state_text)

    if (value_power := power.get("power")) is not None:
        yield from check_levels(
            value_power,
            "power",
            params.get("power"),
            human_readable_func=lambda v: f"{v:.1f} W",
            infoname="Power",
        )


check_plugin_apc_rackpdu_power = CheckPlugin(
    name="apc_rackpdu_power",
    service_name="PDU %s",
    discovery_function=discover_apc_rackpdu_power,
    check_function=check_apc_rackpdu_power,
    check_ruleset_name="el_inphase",
    check_default_parameters={},
)
