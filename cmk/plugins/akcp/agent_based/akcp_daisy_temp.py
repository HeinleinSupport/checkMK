#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from collections.abc import Sequence
from itertools import chain

from cmk.agent_based.v2 import (
    all_of,
    any_of,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    equals,
    exists,
    get_value_store,
    not_exists,
    OIDEnd,
    Service,
    SNMPSection,
    SNMPTree,
    StringTable,
)
from cmk.plugins.lib.temperature import check_temperature, TempParamDict, TempParamType


def discover_akcp_daisy_temp(section: Sequence[StringTable]) -> DiscoveryResult:
    for _port, subport, name, _temp in chain.from_iterable(section):
        # Ignore sensors that are found by the non-daisychaining-version of
        # this check (akcp_sensor_temp)
        if subport not in ["-1", "0"]:
            yield Service(item=name)


def check_akcp_daisy_temp(
    item: str, params: TempParamType, section: Sequence[StringTable]
) -> CheckResult:
    for _port, _subport, name, rawtemp in chain.from_iterable(section):
        if name == item:
            temp = float(rawtemp) / 10
            yield from check_temperature(
                reading=temp,
                params=params,
                unique_name=item,
                value_store=get_value_store(),
            )


def parse_akcp_daisy_temp(string_table: Sequence[StringTable]) -> Sequence[StringTable]:
    return string_table


snmp_section_akcp_daisy_temp = SNMPSection(
    name="akcp_daisy_temp",
    detect=all_of(
        any_of(
            equals(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.3854.1.2.2.1.1"),
            equals(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.3854.1"),
        ),
        not_exists(".1.3.6.1.4.1.3854.2.*"),
        exists(".1.3.6.1.4.1.3854.1.2.2.1.19.*"),
    ),
    fetch=[
        SNMPTree(
            base=".1.3.6.1.4.1.3854.1.2.2.1.19.33.1.2.1",
            oids=[OIDEnd(), "1", "2", "14"],
        ),
        SNMPTree(
            base=".1.3.6.1.4.1.3854.1.2.2.1.19.33.2.2.1",
            oids=[OIDEnd(), "1", "2", "14"],
        ),
        SNMPTree(
            base=".1.3.6.1.4.1.3854.1.2.2.1.19.33.3.2.1",
            oids=[OIDEnd(), "1", "2", "14"],
        ),
        SNMPTree(
            base=".1.3.6.1.4.1.3854.1.2.2.1.19.33.4.2.1",
            oids=[OIDEnd(), "1", "2", "14"],
        ),
        SNMPTree(
            base=".1.3.6.1.4.1.3854.1.2.2.1.19.33.5.2.1",
            oids=[OIDEnd(), "1", "2", "14"],
        ),
        SNMPTree(
            base=".1.3.6.1.4.1.3854.1.2.2.1.19.33.6.2.1",
            oids=[OIDEnd(), "1", "2", "14"],
        ),
        SNMPTree(
            base=".1.3.6.1.4.1.3854.1.2.2.1.19.33.7.2.1",
            oids=[OIDEnd(), "1", "2", "14"],
        ),
        SNMPTree(
            base=".1.3.6.1.4.1.3854.1.2.2.1.19.33.8.2.1",
            oids=[OIDEnd(), "1", "2", "14"],
        ),
    ],
    parse_function=parse_akcp_daisy_temp,
)


check_plugin_akcp_daisy_temp = CheckPlugin(
    name="akcp_daisy_temp",
    service_name="Temperature %s",
    discovery_function=discover_akcp_daisy_temp,
    check_function=check_akcp_daisy_temp,
    check_ruleset_name="temperature",
    check_default_parameters=TempParamDict(levels=(28.0, 32.0)),
)
