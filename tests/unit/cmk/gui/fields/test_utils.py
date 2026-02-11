#!/usr/bin/env python3
# Copyright (C) 2024 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

import pytest

from cmk.gui.fields.utils import tree_to_expr
from cmk.livestatus_client.tables import Hosts


def test_tree_to_expr_eq() -> None:
    result = tree_to_expr({"op": "=", "left": "hosts.name", "right": "example.com"})
    assert repr(result) == "Filter(name = example.com)"


def test_tree_to_expr_neq() -> None:
    result = tree_to_expr({"op": "!=", "left": "hosts.name", "right": "example.com"})
    assert repr(result) == "Filter(name != example.com)"


def test_tree_to_expr_neq_with_table() -> None:
    result = tree_to_expr({"op": "!=", "left": "name", "right": "example.com"}, "hosts")
    assert repr(result) == "Filter(name != example.com)"


def test_tree_to_expr_and() -> None:
    result = tree_to_expr(
        {
            "op": "and",
            "expr": [
                {"op": "=", "left": "hosts.name", "right": "example.com"},
                {"op": "=", "left": "hosts.state", "right": "0"},
            ],
        }
    )
    assert repr(result) == "And(Filter(name = example.com), Filter(state = 0))"


def test_tree_to_expr_or() -> None:
    result = tree_to_expr(
        {
            "op": "or",
            "expr": [
                {"op": "=", "left": "hosts.name", "right": "example.com"},
                {"op": "=", "left": "hosts.name", "right": "heute"},
            ],
        }
    )
    assert repr(result) == "Or(Filter(name = example.com), Filter(name = heute))"


def test_tree_to_expr_not() -> None:
    result = tree_to_expr(
        {"op": "not", "expr": {"op": "=", "left": "hosts.name", "right": "example.com"}}
    )
    assert repr(result) == "Not(Filter(name = example.com))"


def test_tree_to_expr_nested_not() -> None:
    result = tree_to_expr(
        {
            "op": "not",
            "expr": {
                "op": "not",
                "expr": {"op": "=", "left": "hosts.name", "right": "example.com"},
            },
        }
    )
    assert repr(result) == "Not(Not(Filter(name = example.com)))"


def test_tree_to_expr_with_expression_object() -> None:
    result = tree_to_expr({"op": "not", "expr": Hosts.name == "example.com"})
    assert repr(result) == "Not(Filter(name = example.com))"


def test_tree_to_expr_unknown_operator() -> None:
    with pytest.raises(ValueError, match="Unknown operator: no_way"):
        tree_to_expr(
            {"op": "no_way", "expr": {"op": "=", "left": "hosts.name", "right": "example.com"}}
        )
