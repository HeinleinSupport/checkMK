#!/usr/bin/env python3
# Copyright (C) 2020 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
import datetime as dt


def to_timestamp(datetime: dt.datetime) -> int:
    """Convert a datetime object (timezone aware) to a unix-timestamp.

    Args:
        datetime:
            A timezone aware datetime object.

    Returns:
        The unix timestamp of the date.
    """

    if not datetime.tzinfo:
        raise RuntimeError("Only timezone aware dates are allowed.")

    return int(datetime.timestamp())
