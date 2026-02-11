#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

import re

import pytest

# Patterns from the LabelValue / LabelName NewType docstrings
_VALIDATION_VALUE = re.compile(r"(([A-Za-z0-9][-A-Za-z0-9_.]*)?[A-Za-z0-9])?")
_VALIDATION_NAME_PART = re.compile(r"([A-Za-z0-9][-A-Za-z0-9_.]*)?[A-Za-z0-9]")
_VALIDATION_PREFIX_PART = re.compile(
    r"[a-z0-9]([-a-z0-9]*[a-z0-9])?([.][a-z0-9]([-a-z0-9]*[a-z0-9])?)*"
)


@pytest.mark.parametrize(
    "value,expected",
    [
        pytest.param("MyName", True, id="alphanumeric"),
        pytest.param("my.name", True, id="with-dot"),
        pytest.param("123-abc", True, id="digits-dash"),
        pytest.param("a..a", True, id="repeating-dots-ok"),
        pytest.param("", True, id="empty-allowed"),
        pytest.param("a-", False, id="trailing-dash"),
        pytest.param("a&a", False, id="ampersand-not-allowed"),
    ],
)
def test_label_value_validation(value: str, expected: bool) -> None:
    assert bool(_VALIDATION_VALUE.fullmatch(value)) is expected


@pytest.mark.parametrize(
    "prefix,expected",
    [
        pytest.param("a-a", True, id="dns-label"),
        pytest.param("a.a", True, id="two-dns-labels"),
        pytest.param("A", False, id="uppercase-not-allowed"),
        pytest.param(".a", False, id="leading-dot"),
        pytest.param("a..a", False, id="empty-dns-label"),
    ],
)
def test_label_prefix_part_validation(prefix: str, expected: bool) -> None:
    assert bool(_VALIDATION_PREFIX_PART.fullmatch(prefix)) is expected


@pytest.mark.parametrize(
    "name,expected",
    [
        pytest.param("a", True, id="valid-name-only"),
        pytest.param("a/A", True, id="valid-prefix-and-name"),
        pytest.param("/A", False, id="empty-prefix"),
        pytest.param("./a", False, id="dot-prefix"),
        pytest.param("a/a/a", False, id="multiple-slashes"),
    ],
)
def test_label_name_validation(name: str, expected: bool) -> None:
    *prefix_part, name_part = name.split("/", maxsplit=1)
    if len(prefix_part) > 0:
        assert (
            bool(_VALIDATION_PREFIX_PART.fullmatch(prefix_part[0]))
            and bool(_VALIDATION_NAME_PART.fullmatch(name_part))
        ) is expected
    else:
        assert bool(_VALIDATION_NAME_PART.fullmatch(name_part)) is expected
