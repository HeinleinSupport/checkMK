#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

import pytest
from marshmallow import Schema

from cmk.fields import String
from cmk.gui.openapi.restful_objects.validators import PathParamsValidator


def test_verify_marshmallow_params_matching() -> None:
    class Params(Schema):
        bar = String()

    PathParamsValidator.verify_marshmallow_params_presence("/foo/{bar}", Params)


def test_verify_marshmallow_params_no_schema_no_params() -> None:
    PathParamsValidator.verify_marshmallow_params_presence("/foo", None)


def test_verify_marshmallow_params_unused_schema_field() -> None:
    class Params(Schema):
        bar = String()

    with pytest.raises(ValueError, match="not used in path"):
        PathParamsValidator.verify_marshmallow_params_presence("/foo", Params)


def test_verify_marshmallow_params_missing_schema() -> None:
    with pytest.raises(ValueError, match="were not given in schema parameters"):
        PathParamsValidator.verify_marshmallow_params_presence("/foo/{bar}", None)
