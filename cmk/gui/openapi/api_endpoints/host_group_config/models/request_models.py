#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
from typing import Annotated, Self

from pydantic import AfterValidator, model_validator

from cmk.ccc.version import Edition
from cmk.gui.fields.utils import edition_field_description
from cmk.gui.groups import GroupSpec
from cmk.gui.openapi.framework.model import api_field, api_model, ApiOmitted
from cmk.gui.openapi.framework.model.converter import GroupConverter
from cmk.gui.openapi.framework.model.restrict_editions import after_validator_for_customer_field

_CUSTOMER_DESCRIPTION = (
    "By specifying a customer, you configure on which sites the user object will be "
    "available. 'global' will make the object available on all sites."
)


def _to_internal_customer(customer: str) -> str | None:
    # the internal representation of the "global" customer is None
    return None if customer == "global" else customer


@api_model
class CreateHostGroup:
    name: Annotated[
        str,
        AfterValidator(GroupConverter.is_valid_name),
        AfterValidator(GroupConverter("host").not_exists),
    ] = api_field(
        description="A name used as identifier",
        example="windows",
    )
    alias: str = api_field(
        description="The name used for displaying in the GUI.",
        example="Windows Servers",
    )
    customer: str | ApiOmitted = api_field(
        description=edition_field_description(
            _CUSTOMER_DESCRIPTION,
            supported_editions={Edition.ULTIMATEMT},
            field_required=True,
        ),
        example="provider",
        default_factory=ApiOmitted,
    )

    @model_validator(mode="after")
    def validate_customer(self) -> Self:
        after_validator_for_customer_field(customer=self.customer, required_if_supported=True)
        return self

    def to_internal(self) -> GroupSpec:
        details: GroupSpec = {"alias": self.alias}
        if not isinstance(self.customer, ApiOmitted):
            details["customer"] = _to_internal_customer(self.customer)
        return details


def _validate_unique_entries(entries: list[CreateHostGroup]) -> list[CreateHostGroup]:
    # the required fields act as the primary key for duplicate detection, the optional
    # customer field is ignored - same as the uniqueItems check in the marshmallow schema
    seen: set[tuple[str, str]] = set()
    for index, entry in enumerate(entries, start=1):
        key = (entry.name, entry.alias)
        if key in seen:
            raise ValueError(f"Duplicate entry found at entry #{index}: {entry.name!r}")
        seen.add(key)
    return entries


@api_model
class BulkCreateHostGroup:
    entries: Annotated[list[CreateHostGroup], AfterValidator(_validate_unique_entries)] = api_field(
        description="A list of host group entries.",
        example=[{"name": "windows", "alias": "Windows Servers"}],
    )


@api_model
class UpdateHostGroupAttributes:
    alias: str = api_field(
        description="The name used for displaying in the GUI.",
        example="Example Group",
    )
    customer: str | ApiOmitted = api_field(
        description=edition_field_description(
            _CUSTOMER_DESCRIPTION,
            supported_editions={Edition.ULTIMATEMT},
        ),
        example="provider",
        default_factory=ApiOmitted,
    )

    @model_validator(mode="after")
    def validate_customer(self) -> Self:
        after_validator_for_customer_field(customer=self.customer)
        return self

    def to_internal(self) -> GroupSpec:
        details: GroupSpec = {"alias": self.alias}
        if not isinstance(self.customer, ApiOmitted):
            details["customer"] = _to_internal_customer(self.customer)
        return details


@api_model
class UpdateHostGroup:
    name: Annotated[str, AfterValidator(GroupConverter("host").exists)] = api_field(
        description="The name of the host group.",
        example="windows",
    )
    attributes: UpdateHostGroupAttributes = api_field(
        description="The attributes to update.",
    )


@api_model
class BulkUpdateHostGroup:
    entries: list[UpdateHostGroup] = api_field(
        description="A list of host group entries.",
        example=[{"name": "windows", "attributes": {"alias": "Windows Servers"}}],
    )


@api_model
class BulkDeleteHostGroup:
    entries: list[str] = api_field(
        description="A list of host group names.",
        example=["windows", "panels"],
    )
