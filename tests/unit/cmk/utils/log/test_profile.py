#!/usr/bin/env python3
# Copyright (C) 2025 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

import logging
import re

import pytest

from cmk.utils.log.profile import log_duration


def test_log_duration_preserves_return_value(caplog: pytest.LogCaptureFixture) -> None:
    decorator = log_duration(logger=logging.getLogger("test"), level="debug")

    @decorator
    def fetch_site_names() -> list[str]:
        return ["heute"]

    with caplog.at_level(logging.DEBUG):
        assert fetch_site_names() == ["heute"]

    assert (
        re.search(
            r"CALLING\s([a-z0-9._]*)test_profile.test_log_duration_preserves_return_value.<locals>.fetch_site_names",
            caplog.text,
        )
        is not None
    )
    assert (
        re.search(
            r"FINISHED\s([a-z0-9._]*)test_profile.test_log_duration_preserves_return_value.<locals>.fetch_site_names",
            caplog.text,
        )
        is not None
    )


def test_log_duration_wraps_existing_function() -> None:
    decorator = log_duration(logger=logging.getLogger("test"), level="debug")

    @decorator
    def fetch_site_names() -> list[str]:
        return ["heute"]

    assert decorator(len)(fetch_site_names()) == 1
