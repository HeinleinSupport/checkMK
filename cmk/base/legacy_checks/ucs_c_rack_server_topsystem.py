#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

# exemplary output of the special agent ucs_bladecenter (separator is <TAB> and means tabulator):
#
# <<<ucsc_topsystem:sep(9)>>>
# topSystem<TAB>dn sys<TAB>address 192.168.1.1<TAB>currentTime Wed Feb  6 09:12:12 2019<TAB>mode stand-alone<TAB>name CIMC-istreamer2a-etn


import time

from cmk.agent_based.legacy.v0_unstable import LegacyCheckDefinition

check_info = {}


def parse_ucs_c_rack_server_topsystem(string_table):
    """
    Input: Single line string_table with a rack server topsystem information.
    Output: Returns dict with dn, address, current time, mode and name as keys (with corresponding values).
    """

    def format_data_and_time(date_and_time):
        """Converts date and time and returns in time format.

        E.g. Wed Feb  6 09:12:12 2019 -> 2019-02-06 09:12:12
        """
        # time.strptime('Jun 1 2005  1:33PM', '%b %d %Y %I:%M%p')
        struct_time = time.strptime(date_and_time[4:], "%b %d %H:%M:%S %Y")
        formatted = time.strftime("%Y-%m-%d %H:%M:%S", struct_time)
        return formatted

    parsed = []
    # The element count of string_table lines is under our control (agent output) and
    # ensured to have expected length. It is ensured that elements contain a
    # string. No bad case handling required here.
    for _, dn, ip, date_and_time, mode, name in string_table:
        # If more than one string_table line given or in case of unexpected string_table list element format the
        # parsed dict will be empty.
        parsed.extend(
            [
                ("DN", dn.replace("dn ", "")),
                ("IP", ip.replace("address ", "")),
                ("Mode", mode.replace("mode ", "")),
                ("Name", name.replace("name ", "")),
            ]
        )
        try:
            date_time_value = format_data_and_time(date_and_time.replace("currentTime ", ""))
        except ValueError:
            # indicate date and time format not supported
            date_time_value = "unknown[%s]" % date_and_time[4:]
        parsed.append(("Date and time", date_time_value))
    return parsed


def inventory_ucs_c_rack_server_topsystem(parsed):
    if parsed:
        return [(None, None)]
    return []


# @get_parsed_item_data
def check_ucs_c_rack_server_topsystem(item, _no_params, data):
    for title, value in data:
        yield 0, f"{title}: {value}"


check_info["ucs_c_rack_server_topsystem"] = LegacyCheckDefinition(
    name="ucs_c_rack_server_topsystem",
    parse_function=parse_ucs_c_rack_server_topsystem,
    service_name="UCS C-Series Rack Server TopSystem Info",
    discovery_function=inventory_ucs_c_rack_server_topsystem,
    check_function=check_ucs_c_rack_server_topsystem,
)
