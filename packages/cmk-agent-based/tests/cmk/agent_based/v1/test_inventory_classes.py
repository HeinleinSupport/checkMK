#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
import pytest

from cmk.agent_based.v1 import Attributes, TableRow


@pytest.mark.parametrize("path", [["a", 23], ("a", "b")])
def test_common_raise_path_type(path: object) -> None:
    with pytest.raises(TypeError):
        _ = TableRow(path=path, key_columns={})  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        _ = Attributes(path=path)  # type: ignore[arg-type]


def test_common_kwarg_only() -> None:
    with pytest.raises(TypeError):
        _ = Attributes(["a"])  # type: ignore[misc]
    with pytest.raises(TypeError):
        _ = TableRow(["a"], key_columns={"ding": "dong"})  # type: ignore[misc]


def test_atrributes_wrong_types() -> None:
    with pytest.raises(TypeError):
        _ = Attributes(
            path=["software", "os"],
            inventory_attributes={"version": (42, 23)},  # type: ignore[dict-item]
        )


def test_attributes_duplicate_keys() -> None:
    with pytest.raises(ValueError):
        _ = Attributes(
            path=["software", "os"],
            inventory_attributes={"version": "42"},
            status_attributes={"version": "42"},
        )


def test_attributes_instanciated() -> None:
    attr = Attributes(
        path=["software", "os"],
        status_attributes={"vendor": "emmentaler"},
        inventory_attributes={"version": "42"},
    )

    assert attr.path == ["software", "os"]
    assert attr.status_attributes == {"vendor": "emmentaler"}
    assert attr.inventory_attributes == {"version": "42"}
    assert repr(attr) == (
        "Attributes("
        "path=['software', 'os'], "
        "inventory_attributes={'version': '42'}, "
        "status_attributes={'vendor': 'emmentaler'})"
    )

    attr2 = Attributes(
        path=["software", "os"],
        status_attributes={"vendor": "camembert"},
        inventory_attributes={"version": "42"},
    )
    assert attr == attr  # noqa: PLR0124
    assert attr2 != attr


def test_tablerow_missing_key_columns() -> None:
    with pytest.raises(TypeError):
        _ = TableRow(path=["hardware"], key_columns=None)  # type: ignore[arg-type]
        _ = TableRow(path=["hardware"], key_columns={})


def test_tablerow_wrong_types() -> None:
    with pytest.raises(TypeError):
        _ = TableRow(path=["hardware"], key_columns={23: 42})  # type: ignore[dict-item]


def test_tablerow_conflicting_keys() -> None:
    with pytest.raises(ValueError):
        _ = TableRow(
            path=["hardware"],
            key_columns={"foo": "bar"},
            status_columns={"foo": "bar"},
        )


def test_tablerow_instanciated() -> None:
    table_row = TableRow(
        path=["software", "os"],
        key_columns={"foo": "bar"},
        status_columns={"packages": 42},
        inventory_columns={"vendor": "emmentaler"},
    )

    assert table_row.path == ["software", "os"]
    assert table_row.key_columns == {"foo": "bar"}
    assert table_row.status_columns == {"packages": 42}
    assert table_row.inventory_columns == {"vendor": "emmentaler"}
    assert repr(table_row) == (
        "TableRow("
        "path=['software', 'os'], "
        "key_columns={'foo': 'bar'}, "
        "inventory_columns={'vendor': 'emmentaler'}, "
        "status_columns={'packages': 42})"
    )

    table_row2 = TableRow(
        path=["software", "os"],
        key_columns={"foo": "bar"},
        status_columns={"packages": 42},
        inventory_columns={"vendor": "gorgonzola"},
    )
    assert table_row == table_row  # noqa: PLR0124
    assert table_row2 != table_row
