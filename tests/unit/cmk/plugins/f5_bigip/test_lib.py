#!/usr/bin/env python3
# Copyright (C) 2024 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

import re

import pytest

from cmk.plugins.f5_bigip.lib import VERSION_GE_V11_2_PATTERN, VERSION_GE_V11_PATTERN


@pytest.mark.parametrize(
    "version,expected",
    [
        pytest.param("9.2.5", False, id="v9-no-match"),
        pytest.param("10.2.0", False, id="v10.2.0-no-match"),
        pytest.param("10.2.4", False, id="v10.2.4-no-match"),
        pytest.param("11,2.4", False, id="comma-separator-no-match"),
        pytest.param("11.2-4", False, id="dash-separator-no-match"),
        pytest.param("11.4.0", True, id="v11.4.0"),
        pytest.param("11.4.1", True, id="v11.4.1"),
        pytest.param("11.5.1", True, id="v11.5.1"),
        pytest.param("11.5.4", True, id="v11.5.4"),
        pytest.param("11.6.0", True, id="v11.6.0"),
        pytest.param("12.0.0", True, id="v12.0.0"),
        pytest.param("12.1.0", True, id="v12.1.0"),
        pytest.param("12.1.1", True, id="v12.1.1"),
        pytest.param("13.1.0.1", True, id="v13.1.0.1"),
    ],
)
def test_version_ge_v11_2_pattern(version: str, expected: bool) -> None:
    assert bool(re.match(VERSION_GE_V11_2_PATTERN, version)) is expected


@pytest.mark.parametrize(
    "version,expected",
    [
        pytest.param("9.2.5", False, id="v9-no-match"),
        pytest.param("10.2.0", False, id="v10.2.0-no-match"),
        pytest.param("10.2.4", False, id="v10.2.4-no-match"),
        pytest.param("10.99.2", False, id="v10.99-no-match"),
        pytest.param("11-2", False, id="dash-separator-no-match"),
        pytest.param("11.0.1", True, id="v11.0.1"),
        pytest.param("11.4.0", True, id="v11.4.0"),
        pytest.param("11.4.1", True, id="v11.4.1"),
        pytest.param("11.5.4", True, id="v11.5.4"),
        pytest.param("11.6.0", True, id="v11.6.0"),
        pytest.param("12.1.0", True, id="v12.1.0"),
        pytest.param("12.1.1", True, id="v12.1.1"),
        pytest.param("13.1.0.1", True, id="v13.1.0.1"),
    ],
)
def test_version_ge_v11_pattern(version: str, expected: bool) -> None:
    assert bool(re.match(VERSION_GE_V11_PATTERN, version)) is expected
