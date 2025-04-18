#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

# Example output of multi-unit stack (SS5500-EL, etc):
# SNMPv2-SMI::enterprises.43.45.1.6.1.1.1.3.65536 = Gauge32: 11
#
# Example outpout of multi-slot switche (SS8800 etc):
# SNMPv2-SMI::enterprises.43.45.1.6.1.1.1.3.0 = Gauge32: 11
# [...]
# SNMPv2-SMI::enterprises.43.45.1.6.1.1.1.3.12 = Gauge32: 16
# SNMPv2-SMI::enterprises.43.45.1.6.1.1.1.3.13 = Gauge32: 16


# We do not want to use the end OID as item since.
# We prefer "Switch 1 CPU 1" over "65537"...


from cmk.agent_based.legacy.v0_unstable import LegacyCheckDefinition
from cmk.agent_based.v2 import contains, OIDEnd, SNMPTree, StringTable

check_info = {}


def h3c_lanswitch_cpu_genitem(item):
    # decide switch class here (stacked or standalone/modular)
    cpuid = int(item)

    # if we have a cpuid lower than (hopefully) 256 it is not hashed with a unit ID
    if cpuid < 256:
        switchid = 1
        cputype = "Slot"
        cpunum = cpuid

    # othwise, if above 64k it is a known stackable switch
    elif cpuid >= 65536:
        switchid = cpuid // 65536
        cputype = "CPU"
        cpunum = cpuid % 65536

    # if we end up here 3com has added another hash method.
    else:
        switchid = 1
        cputype = "Unknown"
        cpunum = cpuid
    return "Switch %d %s %d" % (switchid, cputype, cpunum)


def inventory_h3c_lanswitch_cpu(info):
    return [(h3c_lanswitch_cpu_genitem(line[0]), {}) for line in info]


def check_h3c_lanswitch_cpu(item, params, info):
    warn, crit = params["levels"]
    for line in info:
        if h3c_lanswitch_cpu_genitem(line[0]) == item:
            util = int(line[1])
            infotext = "average usage was %d%% over last 5 minutes." % util
            perfdata = [("usage", util, warn, crit, 0, 100)]

            if util > crit:
                return (2, infotext, perfdata)
            if util > warn:
                return (1, infotext, perfdata)
            return (0, infotext, perfdata)

    return (3, "%s not found" % item)


def parse_h3c_lanswitch_cpu(string_table: StringTable) -> StringTable:
    return string_table


check_info["h3c_lanswitch_cpu"] = LegacyCheckDefinition(
    name="h3c_lanswitch_cpu",
    parse_function=parse_h3c_lanswitch_cpu,
    detect=contains(".1.3.6.1.2.1.1.1.0", "3com s"),
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.43.45.1.6.1.1.1",
        oids=[OIDEnd(), "3"],
    ),
    service_name="CPU Utilization %s",
    discovery_function=inventory_h3c_lanswitch_cpu,
    check_function=check_h3c_lanswitch_cpu,
    check_default_parameters={"levels": (50, 75)},
)
