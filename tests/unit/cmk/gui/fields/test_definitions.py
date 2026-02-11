#!/usr/bin/env python3
# Copyright (C) 2024 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

import pytest
from marshmallow import Schema, ValidationError

from cmk.gui.fields.definitions import (
    _ListOfColumns,
    _LiveStatusColumn,
    ExprSchema,
    NotExprSchema,
    Timestamp,
)
from cmk.gui.fields.utils import BaseSchema
from cmk.livestatus_client.tables import Hosts


def test_not_expr_schema_load() -> None:
    input_expr = {"op": "=", "left": "hosts.name", "right": "foo"}
    q = {"op": "not", "expr": input_expr}
    schema = NotExprSchema()
    schema.context = {"table": Hosts}
    assert schema.load(q) == q


def test_expr_schema_load_nested() -> None:
    q = {
        "op": "and",
        "expr": [
            {
                "op": "not",
                "expr": {
                    "op": "or",
                    "expr": [
                        {"op": "=", "left": "name", "right": "foo"},
                        {"op": "=", "left": "name", "right": "bar"},
                    ],
                },
            },
        ],
    }
    schema = ExprSchema(context={"table": Hosts})

    assert schema.load(q) == schema.load(q)


def test_expr_schema_unknown_column() -> None:
    q = {"op": "=", "left": "foo", "right": "bar"}
    schema = ExprSchema(context={"table": Hosts})
    with pytest.raises(ValidationError, match="has no column 'foo'"):
        schema.load(q)


def test_list_of_columns_deserialize() -> None:
    cols = _ListOfColumns(_LiveStatusColumn(table=Hosts), table=Hosts)
    result = cols.deserialize(["name", "alias"])
    assert repr(result) == "[Column(hosts.name: string), Column(hosts.alias: string)]"


def test_list_of_columns_with_mandatory() -> None:
    cols = _ListOfColumns(_LiveStatusColumn(table=Hosts), table=Hosts, mandatory=[str(Hosts.name)])
    result = cols.deserialize(["alias"])
    assert repr(result) == "[Column(hosts.name: string), Column(hosts.alias: string)]"


def test_list_of_columns_schema_load() -> None:
    class FooSchema(BaseSchema):
        columns = _ListOfColumns(
            _LiveStatusColumn(table=Hosts), table=Hosts, mandatory=[str(Hosts.name)]
        )

    schema = FooSchema()
    result = schema.load({"columns": ["alias"]})
    assert repr(result["columns"]) == "[Column(hosts.name: string), Column(hosts.alias: string)]"


def test_livestatus_column_valid() -> None:
    assert _LiveStatusColumn(table=Hosts).deserialize("name") == "name"


def test_livestatus_column_invalid() -> None:
    with pytest.raises(ValidationError, match="Unknown column: hosts.bar"):
        _LiveStatusColumn(table=Hosts).deserialize("bar")


def test_timestamp_dump() -> None:
    class TestSchema(Schema):
        ts_field = Timestamp()

    schema = TestSchema()
    assert schema.dump({"ts_field": "0.0"}) == {"ts_field": "1970-01-01T00:00:00+00:00"}
    assert schema.dump({"ts_field": 1622620683.60371}) == {
        "ts_field": "2021-06-02T07:58:03.603710+00:00"
    }


def test_timestamp_round_trip() -> None:
    class TestSchema(Schema):
        ts_field = Timestamp()

    schema = TestSchema()
    value = {"ts_field": 0.0}
    dumped = schema.dump(value)
    assert dumped == {"ts_field": "1970-01-01T00:00:00+00:00"}
    loaded = schema.load(dumped)
    assert loaded == value


def test_timestamp_invalid_value() -> None:
    class TestSchema(Schema):
        ts_field = Timestamp()

    schema = TestSchema()
    with pytest.raises(ValidationError):
        schema.load({"ts_field": "foo"})
