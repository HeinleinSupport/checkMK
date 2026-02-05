#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from cmk.utils.licensing.community_handler import CommunityLicensingHandler
from cmk.utils.licensing.handler import LicenseState, UserEffect


def test_community_licensing_handler() -> None:
    community_handler = CommunityLicensingHandler()
    assert community_handler.state is LicenseState.LICENSED
    assert community_handler.message == ""
    assert community_handler.effect_core(1, 2) == UserEffect(header=None, email=None, block=None)
    assert community_handler.effect() == UserEffect(header=None, email=None, block=None)
