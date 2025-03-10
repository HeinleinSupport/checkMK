#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


from cmk.plugins.collection.agent_based import ceph_df


def test_sanitize_line() -> None:
    assert ceph_df._sanitize_line(
        [
            "cephfs_data",
            "1",
            "N/A",
            "N/A",
            "1.6",
            "GiB",
            "1.97",
            "77",
            "GiB",
            "809",
            "809",
            "33",
            "B",
            "177",
            "KiB",
            "4.7",
            "GiB",
        ]
    ) == [
        "cephfs_data",
        "1",
        "N/A",
        "N/A",
        "1.6GiB",
        "1.97",
        "77GiB",
        "809",
        "809",
        "33B",
        "177KiB",
        "4.7GiB",
    ]
