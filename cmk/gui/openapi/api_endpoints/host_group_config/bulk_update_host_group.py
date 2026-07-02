#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
from cmk.gui.openapi.endpoints.utils import update_groups
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

from ._family import HOST_GROUP_FAMILY
from ._utils import make_pending_changes, RW_PERMISSIONS, serialize_host_group_collection
from .models.request_models import BulkUpdateHostGroup
from .models.response_models import HostGroupCollectionModel


def bulk_update_host_group_v1(
    api_context: ApiContext, body: BulkUpdateHostGroup
) -> HostGroupCollectionModel:
    """Bulk update host groups

    Please be aware that when doing bulk updates, it is not possible to prevent the
    [Updating Values]("lost update problem"), which is normally prevented by the ETag locking
    mechanism. Use at your own risk
    """
    api_context.user.need_permission("wato.edit")
    api_context.user.need_permission("wato.groups")
    entries = [
        {"name": entry.name, "attributes": entry.attributes.to_internal()} for entry in body.entries
    ]
    updated_host_groups = update_groups(
        "host",
        entries,
        pprint_value=api_context.config.wato_pprint_config,
        pending_changes=make_pending_changes(api_context),
    )
    return serialize_host_group_collection(api_context, updated_host_groups)


ENDPOINT_BULK_UPDATE_HOST_GROUP = VersionedEndpoint(
    metadata=EndpointMetadata(
        path=domain_type_action_href("host_group_config", "bulk-update"),
        link_relation="cmk/bulk_update",
        method="put",
    ),
    permissions=EndpointPermissions(required=RW_PERMISSIONS),
    doc=EndpointDoc(family=HOST_GROUP_FAMILY.name),
    versions={APIVersion.V1: EndpointHandler(handler=bulk_update_host_group_v1)},
)
