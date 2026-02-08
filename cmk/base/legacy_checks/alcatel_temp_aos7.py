#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from collections.abc import Mapping

from cmk.agent_based.v2 import (
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    get_value_store,
    Service,
    SimpleSNMPSection,
    SNMPTree,
    StringTable,
)
from cmk.plugins.alcatel.lib import DETECT_ALCATEL_AOS7
from cmk.plugins.lib.temperature import check_temperature, TempParamDict, TempParamType

type Section = Mapping[str, int]


def parse_alcatel_aos7_temp(string_table: StringTable) -> Section:
    if not string_table:
        return {}
    most_recent_values = string_table[-1]
    parsed: dict[str, int] = {}
    board_not_connected_value = 0
    boards = (
        "CPMA",
        "CFMA",
        "CPMB",
        "CFMB",
        "CFMC",
        "CFMD",
        "FTA",
        "FTB",
        "NI1",
        "NI2",
        "NI3",
        "NI4",
        "NI5",
        "NI6",
        "NI7",
        "NI8",
    )
    for index, board in enumerate(boards):
        try:
            temperature = int(most_recent_values[index])
        except ValueError:
            continue
        if temperature != board_not_connected_value:
            parsed[board] = temperature
    return parsed


def check_alcatel_aos7_temp(item: str, params: TempParamType, section: Section) -> CheckResult:
    if not (data := section.get(item)):
        return
    yield from check_temperature(
        reading=float(data),
        params=params,
        unique_name=item,
        value_store=get_value_store(),
    )


def discover_alcatel_temp_aos7(section: Section) -> DiscoveryResult:
    yield from (Service(item=item) for item in section)


snmp_section_alcatel_temp_aos7 = SimpleSNMPSection(
    name="alcatel_temp_aos7",
    detect=DETECT_ALCATEL_AOS7,
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.6486.801.1.1.1.3.1.1.3.1",
        oids=[
            "8",
            "9",
            "10",
            "11",
            "12",
            "13",
            "14",
            "15",
            "16",
            "17",
            "18",
            "19",
            "20",
            "21",
            "22",
            "23",
        ],
    ),
    parse_function=parse_alcatel_aos7_temp,
)


check_plugin_alcatel_temp_aos7 = CheckPlugin(
    name="alcatel_temp_aos7",
    service_name="Temperature Board %s",
    discovery_function=discover_alcatel_temp_aos7,
    check_function=check_alcatel_aos7_temp,
    check_ruleset_name="temperature",
    check_default_parameters=TempParamDict(levels=(45.0, 50.0)),
)
