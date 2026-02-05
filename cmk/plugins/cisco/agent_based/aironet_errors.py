#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


import time

from cmk.agent_based.v2 import (
    any_of,
    check_levels,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    equals,
    get_rate,
    get_value_store,
    OIDEnd,
    Service,
    SimpleSNMPSection,
    SNMPTree,
    StringTable,
)


def discover_aironet_errors(section: StringTable) -> DiscoveryResult:
    yield from (Service(item=line[0]) for line in section)


def check_aironet_errors(item: str, section: StringTable) -> CheckResult:
    for line in section:
        if line[0] == item:
            yield from check_levels(
                get_rate(
                    get_value_store(),
                    f"aironet_errors.{item}",
                    time.time(),
                    int(line[1]),
                    raise_overflow=True,
                ),
                levels_upper=("fixed", (1.0, 10.0)),
                metric_name="errors",
                label="Errors/s",
            )
            return


def parse_aironet_errors(string_table: StringTable) -> StringTable:
    return string_table


snmp_section_aironet_errors = SimpleSNMPSection(
    name="aironet_errors",
    detect=any_of(
        equals(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.9.1.525"),
        equals(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.9.1.618"),
        equals(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.9.1.685"),
        equals(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.9.1.758"),
        equals(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.9.1.1034"),
        equals(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.9.1.1247"),
    ),
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.9.9.272.1.2.1.1.1",
        oids=[OIDEnd(), "2"],
    ),
    parse_function=parse_aironet_errors,
)


check_plugin_aironet_errors = CheckPlugin(
    name="aironet_errors",
    service_name="MAC CRC errors radio %s",
    discovery_function=discover_aironet_errors,
    check_function=check_aironet_errors,
)
