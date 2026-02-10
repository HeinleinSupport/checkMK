#!/usr/bin/env python3
# Copyright (C) 2024 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from marshmallow import fields

from cmk.bi.lib import create_nested_schema, get_schema_default_config
from cmk.bi.schema import Schema
from cmk.fields import String


def test_create_nested_schema_dump_default() -> None:
    class Foo(Schema):
        field = String()

    nested = create_nested_schema(Foo)
    assert nested.dump_default == {}


def test_get_schema_default_config() -> None:
    class Foo(Schema):
        field = fields.String(dump_default="bar")

    assert get_schema_default_config(Foo) == {"field": "bar"}


def test_get_schema_default_config_with_params() -> None:
    class Foo(Schema):
        field = fields.String(dump_default="bar")

    assert get_schema_default_config(Foo, {"field": "foo", "omit": "this"}) == {"field": "foo"}
