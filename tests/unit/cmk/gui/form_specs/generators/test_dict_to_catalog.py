#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
"""Tests for the flat-catalog converter (``dict_to_catalog``)."""

from cmk.gui.form_specs.generators.dict_to_catalog import Dict2CatalogConverter
from cmk.gui.form_specs.unstable import Catalog
from cmk.rulesets.v1.form_specs import DictElement, Dictionary, String


def test_converter_preserves_element_required_flag() -> None:
    """A DictElement's ``required`` must survive the conversion to a Catalog.

    Regression: the converter used to hard-code ``required=True`` for every element,
    which made optional fields (e.g. the SAML encryption certificate) appear mandatory.
    """
    dictionary = Dictionary(
        elements={
            "mandatory": DictElement(required=True, parameter_form=String()),
            "optional": DictElement(required=False, parameter_form=String()),
        },
    )

    catalog = Dict2CatalogConverter.build_from_dictionary(dictionary).catalog
    assert isinstance(catalog, Catalog)

    topic = next(iter(catalog.elements.values()))
    assert isinstance(topic.elements, dict)
    assert topic.elements["mandatory"].required is True
    assert topic.elements["optional"].required is False


def test_converter_defaults_required_to_false() -> None:
    """DictElement.required defaults to False, and that default is propagated."""
    dictionary = Dictionary(elements={"implicit": DictElement(parameter_form=String())})

    catalog = Dict2CatalogConverter.build_from_dictionary(
        dictionary, headers=[("Group", ["implicit"])]
    ).catalog
    topic = next(iter(catalog.elements.values()))
    assert isinstance(topic.elements, dict)
    assert topic.elements["implicit"].required is False
