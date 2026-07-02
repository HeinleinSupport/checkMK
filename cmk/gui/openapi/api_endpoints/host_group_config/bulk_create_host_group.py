#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
from cmk.gui.openapi.endpoints.utils import fetch_specific_groups, prepare_groups
from cmk.gui.openapi.framework import (
    ApiContext,
    APIVersion,
    EndpointDoc,
    EndpointHandler,
    EndpointMetadata,
    EndpointPermissions,
    VersionedEndpoint,
)
from cmk.gui.openapi.restful_objects.constructors import domain_type_action_href
from cmk.gui.watolib import groups

from ._family import HOST_GROUP_FAMILY
from ._utils import make_pending_changes, RW_PERMISSIONS, serialize_host_group_collection
from .models.request_models import BulkCreateHostGroup
from .models.response_models import HostGroupCollectionModel


def bulk_create_host_group_v1(
    api_context: ApiContext, body: BulkCreateHostGroup
) -> HostGroupCollectionModel:
    """Bulk create host groups"""
    api_context.user.need_permission("wato.edit")
    api_context.user.need_permission("wato.groups")
    entries = [{"name": entry.name, **entry.to_internal()} for entry in body.entries]
    host_group_details = prepare_groups("host", entries)

    host_group_names = []
    for group_name, group_details in host_group_details.items():
        groups.add_group(
            group_name,
            "host",
            group_details,
            pprint_value=api_context.config.wato_pprint_config,
            pending_changes=make_pending_changes(api_context),
        )
        host_group_names.append(group_name)

    return serialize_host_group_collection(
        api_context, fetch_specific_groups(host_group_names, "host")
    )


ENDPOINT_BULK_CREATE_HOST_GROUP = VersionedEndpoint(
    metadata=EndpointMetadata(
        path=domain_type_action_href("host_group_config", "bulk-create"),
        link_relation="cmk/bulk_create",
        method="post",
    ),
    permissions=EndpointPermissions(required=RW_PERMISSIONS),
    doc=EndpointDoc(family=HOST_GROUP_FAMILY.name),
    versions={APIVersion.V1: EndpointHandler(handler=bulk_create_host_group_v1)},
)
