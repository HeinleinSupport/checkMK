#!/usr/bin/env python3
# Copyright (C) 2024 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

import pytest
from marshmallow import ValidationError
from marshmallow.validate import Length

from cmk.fields.validators import ValidateAnyOfValidators


def test_validate_any_of_validators_passes() -> None:
    validator = ValidateAnyOfValidators([Length(min=0, max=4), Length(min=6, max=10)])
    validator("foo")  # passes first validator
    validator("barbarbar")  # passes second validator


def test_validate_any_of_validators_fails() -> None:
    validator = ValidateAnyOfValidators([Length(min=0, max=4), Length(min=6, max=10)])
    with pytest.raises(ValidationError) as exc_info:
        validator("12345")
    assert "Any of this needs to be true:" in str(exc_info.value)
