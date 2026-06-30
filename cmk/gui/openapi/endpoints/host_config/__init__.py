#!/usr/bin/env python3
# Copyright (C) 2020 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
"""Shared host serialization helpers for marshmallow endpoints.

The host_config endpoints have been migrated to the new versioned framework
(``cmk.gui.openapi.api_endpoints.host_config``). This module only retains the
marshmallow host-serialization helpers and the host query parameter that the
still-marshmallow ``folder_config`` family reuses for its "hosts in a folder"
endpoint. The folder/host response schemas live in ``response_schemas.py``.
"""

# mypy: disable-error-code="no-any-return"

from collections.abc import Callable, Iterable
from typing import Any

from cmk import fields
from cmk.ccc.hostaddress import HostName
from cmk.gui.fields.fields_filter import FieldsFilter, make_filter
from cmk.gui.http import Response
from cmk.gui.openapi.endpoints.utils import folder_slug
from cmk.gui.openapi.restful_objects import constructors
from cmk.gui.openapi.restful_objects.type_defs import DomainObject, LinkType
from cmk.gui.openapi.utils import serve_json
from cmk.gui.watolib.hosts_and_folders import Host

EFFECTIVE_ATTRIBUTES = {
    "effective_attributes": fields.Boolean(
        load_default=False,
        required=False,
        example=False,
        description=(
            "Show all effective attributes on hosts, not just the attributes which were set on "
            "this host specifically. This includes all attributes of all of this host's parent "
            "folders."
        ),
    )
}


def host_fields_filter(
    *, is_collection: bool, include_links: bool, effective_attributes: bool
) -> FieldsFilter:
    response_fields_filters: dict[str, FieldsFilter] = {}
    if not include_links:
        response_fields_filters["links"] = make_filter(this_is="excluded")
    if not effective_attributes:
        response_fields_filters["extensions"] = make_filter(
            exclude={"effective_attributes": make_filter(this_is="excluded")}
        )

    if not response_fields_filters:
        # no filters, all fields are included
        return make_filter(this_is="included")

    fields_filter = make_filter(exclude=response_fields_filters)
    if not is_collection:
        return fields_filter

    return make_filter(exclude={"value": fields_filter})


def serve_host_collection(
    hosts: Iterable[Host], *, fields_filter: FieldsFilter | None = None
) -> Response:
    return serve_json(_host_collection(hosts, fields_filter=fields_filter))


def _host_collection(
    hosts: Iterable[Host],
    *,
    fields_filter: FieldsFilter | None = None,
) -> dict[str, Any]:
    fields_filter = fields_filter or host_fields_filter(
        is_collection=True, include_links=False, effective_attributes=False
    )
    value_filter = fields_filter.get_nested_fields("value")
    return fields_filter.apply(
        {
            "id": "host",
            "domainType": "host_config",
            "value": (
                [
                    serialize_host(
                        host,
                        fields_filter=value_filter,
                    )
                    for host in hosts
                ]
                if value_filter.is_included()
                else None
            ),
            "links": [constructors.link_rel("self", constructors.collection_href("host_config"))],
        }
    )


agent_links_hook: Callable[[HostName], list[LinkType]] = lambda h: []


def serialize_host(
    host: Host,
    *,
    fields_filter: FieldsFilter,
) -> DomainObject:
    extensions = (
        {
            "folder": "/" + host.folder().path(),
            "attributes": host.attributes,
            "effective_attributes": (
                host.effective_attributes()
                if "extensions.effective_attributes" in fields_filter
                else None
            ),
            "is_cluster": host.is_cluster(),
            "is_offline": host.is_offline(),
            "cluster_nodes": host.cluster_nodes(),
        }
        if "extensions" in fields_filter
        else None
    )

    if "links" in fields_filter:
        links = [
            constructors.link_rel(
                rel="cmk/folder_config",
                href=constructors.object_href("folder_config", folder_slug(host.folder())),
                method="get",
                title="The folder config of the host.",
            ),
        ] + agent_links_hook(host.name())
    else:
        links = []

    return constructors.domain_object(
        domain_type="host_config",
        identifier=host.id(),
        title=host.alias() or host.name(),
        links=links,
        extensions=extensions,
        include_links="links" in fields_filter,
    )
