#!/usr/bin/env python3
# Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
from cmk.gui.openapi.framework.registry import VersionedEndpointRegistry
from cmk.gui.openapi.restful_objects.endpoint_family import EndpointFamilyRegistry

from ._family import HOST_GROUP_FAMILY
from .bulk_create_host_group import ENDPOINT_BULK_CREATE_HOST_GROUP
from .bulk_delete_host_group import ENDPOINT_BULK_DELETE_HOST_GROUP
from .bulk_update_host_group import ENDPOINT_BULK_UPDATE_HOST_GROUP
from .create_host_group import ENDPOINT_CREATE_HOST_GROUP
from .delete_host_group import ENDPOINT_DELETE_HOST_GROUP
from .list_host_groups import ENDPOINT_LIST_HOST_GROUPS
from .show_host_group import ENDPOINT_SHOW_HOST_GROUP
from .update_host_group import ENDPOINT_UPDATE_HOST_GROUP


def register(
    versioned_endpoint_registry: VersionedEndpointRegistry,
    endpoint_family_registry: EndpointFamilyRegistry,
) -> None:
    endpoint_family_registry.register(HOST_GROUP_FAMILY)
    versioned_endpoint_registry.register(ENDPOINT_CREATE_HOST_GROUP)
    versioned_endpoint_registry.register(ENDPOINT_BULK_CREATE_HOST_GROUP)
    versioned_endpoint_registry.register(ENDPOINT_LIST_HOST_GROUPS)
    versioned_endpoint_registry.register(ENDPOINT_SHOW_HOST_GROUP)
    versioned_endpoint_registry.register(ENDPOINT_UPDATE_HOST_GROUP)
    versioned_endpoint_registry.register(ENDPOINT_BULK_UPDATE_HOST_GROUP)
    versioned_endpoint_registry.register(ENDPOINT_DELETE_HOST_GROUP)
    versioned_endpoint_registry.register(ENDPOINT_BULK_DELETE_HOST_GROUP)
