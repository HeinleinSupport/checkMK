#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
from cmk.gui.openapi.endpoints.utils import build_group_list
from cmk.gui.openapi.framework import (
    ApiContext,
    APIVersion,
    EndpointDoc,
    EndpointHandler,
    EndpointMetadata,
    EndpointPermissions,
    VersionedEndpoint,
)
from cmk.gui.openapi.restful_objects.constructors import collection_href
from cmk.gui.watolib.groups_io import load_host_group_information

from ._family import HOST_GROUP_FAMILY
from ._utils import PERMISSIONS, serialize_host_group_collection
from .models.response_models import HostGroupCollectionModel


def list_host_groups_v1(api_context: ApiContext) -> HostGroupCollectionModel:
    """Show all host groups"""
    api_context.user.need_permission("wato.groups")
    return serialize_host_group_collection(
        api_context, build_group_list(load_host_group_information())
    )


ENDPOINT_LIST_HOST_GROUPS = VersionedEndpoint(
    metadata=EndpointMetadata(
        path=collection_href("host_group_config"),
        link_relation=".../collection",
        method="get",
    ),
    permissions=EndpointPermissions(required=PERMISSIONS),
    doc=EndpointDoc(family=HOST_GROUP_FAMILY.name),
    versions={APIVersion.V1: EndpointHandler(handler=list_host_groups_v1)},
)
