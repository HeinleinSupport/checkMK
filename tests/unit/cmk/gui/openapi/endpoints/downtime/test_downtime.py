#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

import json

import pytest

from cmk.gui import sites
from cmk.gui.fields.utils import tree_to_expr
from cmk.gui.openapi.endpoints.downtime import DowntimeParameter
from cmk.gui.openapi.restful_objects.params import marshmallow_to_openapi
from cmk.gui.session import SuperUserContext
from cmk.livestatus_client.queries import Query
from cmk.livestatus_client.tables.downtimes import Downtimes
from cmk.livestatus_client.testing import MockLiveStatusConnection


@pytest.mark.usefixtures("request_context")
def test_show_downtimes_query(mock_livestatus: MockLiveStatusConnection) -> None:
    with mock_livestatus(expect_status_query=True) as live, SuperUserContext():
        live.expect_query(
            "GET downtimes\n"
            "Columns: host_name type\n"
            "Filter: host_name = example.com\n"
            "Filter: type = 0\n"
            "And: 2"
        )
        q = Query([Downtimes.host_name, Downtimes.type])
        q = q.filter(
            tree_to_expr(
                json.loads(marshmallow_to_openapi([DowntimeParameter], "query")[0]["example"]),
                "downtimes",
            )
        )
        assert list(q.iterate(sites.live())) == []
