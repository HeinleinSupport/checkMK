#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from typing import Final

from cmk.agent_based.v2 import startswith

DETECT = startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.25597.1")


STATUS_MAP: Final = {
    "good": (0, "good"),
    "ok": (0, "OK"),
}

DISK_STATUS_MAP: Final = {
    "online": (0, "online"),
}

HEALTH_MAP: Final = {
    "1": (0, "healthy"),
    "2": (2, "unhealthy"),
}
