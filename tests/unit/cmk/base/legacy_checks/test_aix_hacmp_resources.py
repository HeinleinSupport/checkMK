#!/usr/bin/env python3
# Copyright (C) 2025 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

# mypy: disable-error-code="misc"

from collections.abc import Mapping, Sequence
from typing import Any

import pytest

from cmk.agent_based.v2 import Result, Service, State, StringTable
from cmk.base.legacy_checks.aix_hacmp_resources import (
    check_aix_hacmp_resources,
    discover_aix_hacmp_resources,
    parse_aix_hacmp_resources,
)


@pytest.mark.parametrize(
    "string_table, expected_discoveries",
    [
        (
            [
                [
                    "pdb213rg",
                    "ONLINE",
                    "pasv0450",
                    "non-concurrent",
                    "OHN",
                    "FNPN",
                    "NFB",
                    "ignore",
                    "",
                    "",
                    " ",
                    " ",
                    "",
                    "",
                    "",
                ],
                [
                    "pdb213rg",
                    "OFFLINE",
                    "pasv0449",
                    "non-concurrent",
                    "OHN",
                    "FNPN",
                    "NFB",
                    "ignore",
                    "",
                    "",
                    " ",
                    " ",
                    "",
                    "",
                    "",
                ],
                [
                    "pmon01rg",
                    "ONLINE",
                    "pasv0449",
                    "non-concurrent",
                    "OHN",
                    "FNPN",
                    "NFB",
                    "ignore",
                    "",
                    "",
                    " ",
                    " ",
                    "",
                    "",
                    "",
                ],
                [
                    "pmon01rg",
                    "OFFLINE",
                    "pasv0450",
                    "non-concurrent",
                    "OHN",
                    "FNPN",
                    "NFB",
                    "ignore",
                    "",
                    "",
                    " ",
                    " ",
                    "",
                    "",
                    "",
                ],
            ],
            [Service(item="pdb213rg"), Service(item="pmon01rg")],
        ),
    ],
)
def test_discover_aix_hacmp_resources(
    string_table: StringTable, expected_discoveries: Sequence[Service]
) -> None:
    """Test discovery function for aix_hacmp_resources check."""
    parsed = parse_aix_hacmp_resources(string_table)
    result = list(discover_aix_hacmp_resources(parsed))
    assert sorted(result, key=lambda s: s.item or "") == sorted(
        expected_discoveries, key=lambda s: s.item or ""
    )


@pytest.mark.parametrize(
    "item, params, string_table, expected_results",
    [
        (
            "pdb213rg",
            {"expect_online_on": "first"},
            [
                [
                    "pdb213rg",
                    "ONLINE",
                    "pasv0450",
                    "non-concurrent",
                    "OHN",
                    "FNPN",
                    "NFB",
                    "ignore",
                    "",
                    "",
                    " ",
                    " ",
                    "",
                    "",
                    "",
                ],
                [
                    "pdb213rg",
                    "OFFLINE",
                    "pasv0449",
                    "non-concurrent",
                    "OHN",
                    "FNPN",
                    "NFB",
                    "ignore",
                    "",
                    "",
                    " ",
                    " ",
                    "",
                    "",
                    "",
                ],
                [
                    "pmon01rg",
                    "ONLINE",
                    "pasv0449",
                    "non-concurrent",
                    "OHN",
                    "FNPN",
                    "NFB",
                    "ignore",
                    "",
                    "",
                    " ",
                    " ",
                    "",
                    "",
                    "",
                ],
                [
                    "pmon01rg",
                    "OFFLINE",
                    "pasv0450",
                    "non-concurrent",
                    "OHN",
                    "FNPN",
                    "NFB",
                    "ignore",
                    "",
                    "",
                    " ",
                    " ",
                    "",
                    "",
                    "",
                ],
            ],
            [Result(state=State.OK, summary="online on node pasv0450, offline on node pasv0449")],
        ),
        (
            "pmon01rg",
            {"expect_online_on": "first"},
            [
                [
                    "pdb213rg",
                    "ONLINE",
                    "pasv0450",
                    "non-concurrent",
                    "OHN",
                    "FNPN",
                    "NFB",
                    "ignore",
                    "",
                    "",
                    " ",
                    " ",
                    "",
                    "",
                    "",
                ],
                [
                    "pdb213rg",
                    "OFFLINE",
                    "pasv0449",
                    "non-concurrent",
                    "OHN",
                    "FNPN",
                    "NFB",
                    "ignore",
                    "",
                    "",
                    " ",
                    " ",
                    "",
                    "",
                    "",
                ],
                [
                    "pmon01rg",
                    "ONLINE",
                    "pasv0449",
                    "non-concurrent",
                    "OHN",
                    "FNPN",
                    "NFB",
                    "ignore",
                    "",
                    "",
                    " ",
                    " ",
                    "",
                    "",
                    "",
                ],
                [
                    "pmon01rg",
                    "OFFLINE",
                    "pasv0450",
                    "non-concurrent",
                    "OHN",
                    "FNPN",
                    "NFB",
                    "ignore",
                    "",
                    "",
                    " ",
                    " ",
                    "",
                    "",
                    "",
                ],
            ],
            [Result(state=State.OK, summary="online on node pasv0449, offline on node pasv0450")],
        ),
    ],
)
def test_check_aix_hacmp_resources(
    item: str,
    params: Mapping[str, Any],
    string_table: StringTable,
    expected_results: Sequence[Result],
) -> None:
    """Test check function for aix_hacmp_resources check."""
    parsed = parse_aix_hacmp_resources(string_table)
    result = list(check_aix_hacmp_resources(item, params, parsed))
    assert result == expected_results
