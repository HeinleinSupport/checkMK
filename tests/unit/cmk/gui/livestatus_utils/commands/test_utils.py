#!/usr/bin/env python3
# Copyright (C) 2024 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

import datetime as dt
from zoneinfo import ZoneInfo

import pytest
from dateutil import tz

from cmk.gui.livestatus_utils.commands.utils import to_timestamp


def test_to_timestamp_naive_datetime_raises() -> None:
    with pytest.raises(RuntimeError, match="Only timezone aware dates are allowed."):
        to_timestamp(dt.datetime(2020, 1, 1))


@pytest.mark.parametrize(
    "datetime_obj,expected",
    [
        pytest.param(dt.datetime(2020, 1, 1, tzinfo=tz.tzutc()), 1577836800, id="dateutil-utc"),
        pytest.param(
            dt.datetime(2020, 1, 1, tzinfo=ZoneInfo("UTC")), 1577836800, id="zoneinfo-utc"
        ),
        pytest.param(dt.datetime(2020, 1, 1, tzinfo=ZoneInfo("GMT")), 1577836800, id="gmt"),
        pytest.param(dt.datetime(2020, 1, 1, tzinfo=ZoneInfo("MET")), 1577833200, id="met"),
        pytest.param(
            dt.datetime(2020, 1, 1, tzinfo=ZoneInfo("Asia/Tokyo")), 1577804400, id="tokyo"
        ),
        pytest.param(
            dt.datetime(2020, 1, 1, tzinfo=tz.tzoffset(None, 3600)), 1577833200, id="offset-plus1h"
        ),
        pytest.param(
            dt.datetime(2020, 1, 1, tzinfo=tz.tzoffset(None, -3600)),
            1577840400,
            id="offset-minus1h",
        ),
    ],
)
def test_to_timestamp(datetime_obj: dt.datetime, expected: int) -> None:
    assert to_timestamp(datetime_obj) == expected
