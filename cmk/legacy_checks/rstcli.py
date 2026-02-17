#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from __future__ import annotations

from collections.abc import Generator, Mapping
from typing import Any

# --VOLUME INFORMATION--
#
# Name:              Vol1
# Raid Level:        1
# Size:              932 GB
# StripeSize:        64 KB
# Num Disks:         2
# State:             Normal
# System:            True
# Initialized:       True
# Cache Policy:      Off
#
#
# --DISKS IN VOLUME: Vol1 --
#
# ID:                0-0-0-0
# Type:              Disk
# Disk Type:         SATA Disk
# State:             Normal
# Size:              932 GB
# Free Size:         0 GB
# System Disk:       False
# Usage:             Array member
# Serial Number:     AB-CDEF123456
# Model:             AB CD EF
#
# ID:                0-1-0-0
# Type:              Disk
# Disk Type:         SATA Disk
# State:             Normal
# Size:              932 GB
# Free Size:         0 GB
# System Disk:       False
# Usage:             Array member
# Serial Number:     AB-CDEF123457
# Model:             AB CD EF
# split output into the --xxx-- sections
from cmk.agent_based.legacy.v0_unstable import (
    LegacyCheckDefinition,
    LegacyCheckResult,
    LegacyDiscoveryResult,
)
from cmk.agent_based.v2 import StringTable

check_info = {}

type Section = Mapping[str, Mapping[str, Any]]


def parse_rstcli_sections(
    info: StringTable,
) -> Generator[tuple[str, list[list[str]]] | None]:
    current_section: tuple[str, list[list[str]]] | None = None
    for line in info:
        if line[0].startswith("--"):
            if current_section is not None:
                yield current_section
            current_section = (":".join(line).strip("-").strip(), [])
        elif len(line) < 2:
            # On some systems, there are lines that only consist of
            # a contextless 0. Skip those to avoid parsing errors later.
            continue
        else:
            if current_section is None:
                raise ValueError(" ".join(line))
            current_section[1].append(line)

    yield current_section


# interpret the volumes section
def parse_rstcli_volumes(rows: list[list[str]]) -> dict[str, dict[str, Any]]:
    volumes: dict[str, dict[str, Any]] = {}
    current_volume: dict[str, Any] = {}

    for row in rows:
        if row[0] == "Name":
            current_volume = {}
            volumes[row[1].strip()] = current_volume
        else:
            current_volume[row[0]] = row[1].strip()

    return volumes


# interpret the disks section
def parse_rstcli_disks(rows: list[list[str]]) -> list[dict[str, str]]:
    disks: list[dict[str, str]] = []
    current_disk: dict[str, str] = {}

    for row in rows:
        if row[0] == "ID":
            current_disk = {}
            disks.append(current_disk)

        current_disk[row[0]] = row[1].strip()

    return disks


def parse_rstcli(string_table: StringTable) -> Section:
    if string_table == [["rstcli not found"]]:
        return {}

    volumes: dict[str, dict[str, Any]] = {}
    for section in parse_rstcli_sections(string_table):
        if section is None:
            continue
        if section[0] == "VOLUME INFORMATION":
            volumes.update(parse_rstcli_volumes(section[1]))
        elif section[0].startswith("DISKS IN VOLUME"):
            volume = section[0].split(":")[1].strip()
            volumes[volume]["Disks"] = parse_rstcli_disks(section[1])
        else:
            raise ValueError("invalid section in rstcli output: %s" % section[0])

    return volumes


def discover_rstcli(parsed: Section) -> LegacyDiscoveryResult:
    return [(name, {}) for name in parsed]


# Help! There is no documentation, what are the possible values?
rstcli_states = {
    "Normal": 0,
}


def check_rstcli(item: str, _no_params: object, parsed: Section) -> LegacyCheckResult:
    if not (volume := parsed.get(item)):
        return
    yield (
        rstcli_states.get(volume["State"], 3),
        "RAID %s, %d disks (%s), state %s"
        % (
            volume["Raid Level"],
            int(volume["Num Disks"]),
            volume["Size"],
            volume["State"],
        ),
    )


check_info["rstcli"] = LegacyCheckDefinition(
    name="rstcli",
    parse_function=parse_rstcli,
    service_name="RAID Volume %s",
    discovery_function=discover_rstcli,
    check_function=check_rstcli,
)


def discover_rstcli_pdisks(parsed: Section) -> LegacyDiscoveryResult:
    for key, volume in parsed.items():
        for disk in volume["Disks"]:
            yield "{}/{}".format(key, disk["ID"]), {}


def check_rstcli_pdisks(item: str, _no_params: object, parsed: Section) -> LegacyCheckResult:
    volume, disk_id = item.rsplit("/", 1)

    disks = parsed.get(volume, {}).get("Disks", [])
    for disk in disks:
        if disk["ID"] == disk_id:
            infotext = "{} (unit: {}, size: {}, type: {}, model: {}, serial: {})".format(
                disk["State"],
                volume,
                disk["Size"],
                disk["Disk Type"],
                disk["Model"],
                disk["Serial Number"],
            )
            yield rstcli_states.get(disk["State"], 2), infotext
            return


check_info["rstcli.pdisks"] = LegacyCheckDefinition(
    name="rstcli_pdisks",
    service_name="RAID Disk %s",
    sections=["rstcli"],
    discovery_function=discover_rstcli_pdisks,
    check_function=check_rstcli_pdisks,
)
