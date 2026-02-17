#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


from cmk.agent_based.legacy.v0_unstable import (
    LegacyCheckDefinition,
    LegacyCheckResult,
    LegacyDiscoveryResult,
)
from cmk.agent_based.v2 import SNMPTree, StringTable
from cmk.plugins.hitachi_hnas.lib import DETECT

check_info = {}


def discover_hitachi_hnas_psu(info: StringTable) -> LegacyDiscoveryResult:
    for clusternode, id_, _status in info:
        yield clusternode + "." + id_, {}


def check_hitachi_hnas_psu(item: str, _no_params: object, info: StringTable) -> LegacyCheckResult:
    statusmap = (
        ("", 3),  # 0
        ("ok", 0),  # 1
        ("failed", 2),  # 2
        ("notFitted", 1),  # 3
        ("unknown", 3),  # 4
    )

    for clusternode, id_, status_str in info:
        if clusternode + "." + id_ == item:
            status_int = int(status_str)
            if status_int == 0 or status_int >= len(statusmap):
                yield 3, f"PNode {clusternode} PSU {id_} reports unidentified status {status_int}"
                return
            yield (
                statusmap[status_int][1],
                f"PNode {clusternode} PSU {id_} reports status {statusmap[status_int][0]}",
            )
            return

    yield 3, "SNMP did not report a status of this PSU"


def parse_hitachi_hnas_psu(string_table: StringTable) -> StringTable:
    return string_table


check_info["hitachi_hnas_psu"] = LegacyCheckDefinition(
    name="hitachi_hnas_psu",
    parse_function=parse_hitachi_hnas_psu,
    detect=DETECT,
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.11096.6.1.1.1.2.1.13.1",
        oids=["1", "2", "3"],
    ),
    service_name="PSU %s",
    discovery_function=discover_hitachi_hnas_psu,
    check_function=check_hitachi_hnas_psu,
)
