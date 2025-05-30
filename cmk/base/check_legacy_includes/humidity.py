#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from cmk.agent_based.legacy.v0_unstable import check_levels
from cmk.agent_based.v2 import render, startswith

DETECT = startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.318.1.3")


# ==================================================================================================
# ==================================================================================================
# THIS FUNCTION HAS BEEN MIGRATED TO THE NEW CHECK API (OR IS IN THE PROCESS), PLEASE DO NOT TOUCH
# IT. INSTEAD, MODIFY THE MIGRATED VERSION.
# ==================================================================================================
# ==================================================================================================
def check_humidity(humidity, params):
    if isinstance(params, dict):
        levels = (params.get("levels") or (None, None)) + (
            params.get("levels_lower") or (None, None)
        )
    elif isinstance(params, list | tuple):
        # old params = (crit_low , warn_low, warn, crit)
        levels = (params[2], params[3], params[1], params[0])
    else:
        levels = None

    return check_levels(
        humidity,
        "humidity",
        levels,
        human_readable_func=render.percent,
        boundaries=(0, 100),
    )
