#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

import pytest

from cmk.gui.openapi.utils import param_description
from cmk.gui.watolib.activate_changes import activate_changes_start


def test_param_description_from_foreign_docstring() -> None:
    result = param_description(activate_changes_start.__doc__, "force_foreign_changes")
    assert (
        result
        == "Will activate changes even if the user who made those changes is not the currently logged in user."
    )


def test_param_description_from_own_docstring() -> None:
    result = param_description(param_description.__doc__, "string")
    assert result == "The docstring from which to extract the parameter description."


def test_param_description_missing_param_ignore() -> None:
    assert param_description(param_description.__doc__, "foo", errors="ignore") is None


def test_param_description_missing_param_raise() -> None:
    with pytest.raises(ValueError, match="Parameter 'foo' not found in docstring."):
        param_description(param_description.__doc__, "foo", errors="raise")


def test_param_description_no_docstring_ignore() -> None:
    assert param_description(None, "foo", errors="ignore") is None


def test_param_description_no_docstring_raise() -> None:
    with pytest.raises(ValueError, match="No docstring was given."):
        param_description(None, "foo", errors="raise")
