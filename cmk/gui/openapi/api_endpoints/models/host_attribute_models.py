#!/usr/bin/env python3
# Copyright (C) 2025 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
from dataclasses import dataclass
from typing import Annotated, Literal

from pydantic import AfterValidator

from cmk.utils.agent_registration import HostAgentConnectionMode
from cmk.utils.tags import TagGroupID

from cmk.gui.openapi.api_endpoints.models.attributes import (
    FolderCustomHostAttributesAndTagGroupsModel,
    HostContactGroupModel,
    HostLabels,
    IPMIParametersModel,
    LockedByModel,
    MetaDataModel,
    NetworkScanModel,
    NetworkScanResultModel,
    SNMPCredentialsConverter,
    SNMPCredentialsModel,
)
from cmk.gui.openapi.endpoints._common.host_attribute_schemas import built_in_tag_group_config
from cmk.gui.openapi.framework.model import api_field, ApiOmitted
from cmk.gui.openapi.framework.model.validators import HostAddressValidator, HostValidator
from cmk.gui.watolib.builtin_attributes import HostAttributeLabels, HostAttributeWaitingForDiscovery

HostNameOrIPv4 = Annotated[str, AfterValidator(HostAddressValidator(allow_ipv6=False))]
HostNameOrIPv6 = Annotated[str, AfterValidator(HostAddressValidator(allow_ipv4=False))]


def _validate_tag_id(tag_id: str, built_in_tag_group_id: TagGroupID) -> str:
    tag_group = built_in_tag_group_config.get_tag_group(built_in_tag_group_id)
    assert tag_group is not None

    if tag_id not in [
        None if _tag_id is None else str(_tag_id) for _tag_id in tag_group.get_tag_ids()
    ]:
        raise ValueError(f"Tag ID '{tag_id}' is not valid for tag group '{built_in_tag_group_id}'.")

    return tag_id


@dataclass(kw_only=True)
class BaseHostTagGroupModel:
    tag_address_family: (
        Annotated[str, AfterValidator(lambda v: _validate_tag_id(v, TagGroupID("address_family")))]
        | ApiOmitted
    ) = api_field(description="The IP address family of the host.", example="ip-v4-only")

    tag_agent: (
        Annotated[str, AfterValidator(lambda v: _validate_tag_id(v, TagGroupID("agent")))]
        | ApiOmitted
    ) = api_field(description="Agent and API integrations", example="cmk-agent")

    tag_snmp_ds: (
        Annotated[str, AfterValidator(lambda v: _validate_tag_id(v, TagGroupID("snmp_ds")))]
        | ApiOmitted
    ) = api_field(description="The SNMP data source of the host.", example="snmp-v2")

    tag_piggyback: (
        Annotated[str, AfterValidator(lambda v: _validate_tag_id(v, TagGroupID("piggyback")))]
        | ApiOmitted
    ) = api_field(description="Use piggyback data for this host.", example="piggyback")


@dataclass(kw_only=True)
class BaseHostAttributeModel:
    alias: str | ApiOmitted = api_field(
        description="Add a comment or describe this host", default_factory=ApiOmitted
    )

    site: str | ApiOmitted = api_field(
        description="The site that should monitor this host.", default_factory=ApiOmitted
    )

    parents: list[Annotated[str, AfterValidator(HostValidator.exists)]] | ApiOmitted = api_field(
        description="A list of parents of this host.", default_factory=ApiOmitted
    )

    contactgroups: HostContactGroupModel | ApiOmitted = api_field(
        description="Only members of the contact groups listed here have Setup permission for the host/folder. Optionally, you can make these contact groups automatically monitor contacts. The assignment of hosts to contact groups can also be defined by rules.",
        default_factory=ApiOmitted,
    )

    ipaddress: HostNameOrIPv4 | ApiOmitted = api_field(
        description="An IPv4 address.", default_factory=ApiOmitted
    )

    ipv6address: HostNameOrIPv6 | ApiOmitted = api_field(
        description="An IPv6 address.", default_factory=ApiOmitted
    )

    additional_ipv4addresses: list[HostNameOrIPv4] | ApiOmitted = api_field(
        description="A list of IPv4 addresses.", default_factory=ApiOmitted
    )

    additional_ipv6addresses: list[HostNameOrIPv6] | ApiOmitted = api_field(
        description="A list of IPv6 addresses.", default_factory=ApiOmitted
    )

    # TODO: reevaluate edition handling
    bake_agent_package: bool | ApiOmitted = api_field(
        description="Bake agent packages for this folder even if it is empty.",
        default_factory=ApiOmitted,
    )
    # TODO: reevaluate edition handling
    cmk_agent_connection: str | ApiOmitted = api_field(
        description=(
            "This configures the communication direction of this host.\n"
            f" * `{HostAgentConnectionMode.PULL.value}` (default) - The server will try to contact the monitored host and pull the data by initializing a TCP connection\n"
            f" * `{HostAgentConnectionMode.PUSH.value}` - the host is expected to send the data to the monitoring server without being triggered\n"
        ),
        default_factory=ApiOmitted,
    )

    snmp_community: SNMPCredentialsModel | ApiOmitted = api_field(
        description="The SNMP access configuration. A configured SNMP v1/v2 community here will have precedence over any configured SNMP community rule. For this attribute to take effect, the attribute `tag_snmp_ds` needs to be set first.",
        default_factory=ApiOmitted,
    )

    labels: HostLabels | ApiOmitted = api_field(
        description=f"{HostAttributeLabels().help()} The key is the host label key.",
        default_factory=ApiOmitted,
    )

    waiting_for_discovery: bool | ApiOmitted = api_field(
        description=HostAttributeWaitingForDiscovery()._help_text(),
        default_factory=ApiOmitted,
    )

    network_scan: NetworkScanModel | ApiOmitted = api_field(
        description="Configuration for automatic network scan. Pings will be sent to each IP address in the configured ranges to check if a host is up or down. Each found host will be added to the folder by its host name (if possible) or IP address.",
        default_factory=ApiOmitted,
    )

    management_protocol: Literal["none", "snmp", "ipmi"] | ApiOmitted = api_field(
        description="The protocol used to connect to the management board. Valid options are: 'none' - No management board, 'snmp' - Connect using SNMP, 'ipmi' - Connect using IPMI",
        default_factory=ApiOmitted,
    )

    management_address: Annotated[str, AfterValidator(HostAddressValidator())] | ApiOmitted = (
        api_field(
            description="Address (IPv4, IPv6 or host name) under which the management board can be reached.",
            default_factory=ApiOmitted,
        )
    )

    management_snmp_community: SNMPCredentialsModel | None | ApiOmitted = api_field(
        description="SNMP credentials", default_factory=ApiOmitted
    )

    management_ipmi_credentials: IPMIParametersModel | None | ApiOmitted = api_field(
        description="IPMI credentials", default_factory=ApiOmitted
    )

    locked_by: LockedByModel | ApiOmitted = api_field(
        description="Identity of the entity which locked the locked_attributes. The identity is built out of the Site ID, the program name and the connection ID.",
        default_factory=ApiOmitted,
    )

    locked_attributes: list[str] | ApiOmitted = api_field(
        description="Name of host attributes which are locked in the UI.",
        default_factory=ApiOmitted,
    )

    inventory_failed: bool | ApiOmitted = api_field(
        description="Whether or not the last bulk discovery failed. It is set to True once it fails and unset in case a later discovery succeeds.",
        default_factory=ApiOmitted,
    )

    @staticmethod
    def snmp_community_from_internal(value: str | tuple) -> SNMPCredentialsModel:
        return SNMPCredentialsConverter.from_internal(value)

    @staticmethod
    def snmp_community_to_internal(value: SNMPCredentialsModel) -> str | tuple:
        return SNMPCredentialsConverter.to_internal(value)

    @staticmethod
    def management_protocol_from_internal(value: str | None) -> str:
        if value is None:
            return "none"
        return value

    @staticmethod
    def management_protocol_to_internal(value: str) -> str | None:
        if value == "none":
            return None
        return value


@dataclass(kw_only=True, slots=True)
class HostViewAttributeModel(
    BaseHostAttributeModel, BaseHostTagGroupModel, FolderCustomHostAttributesAndTagGroupsModel
):
    network_scan_result: NetworkScanResultModel | ApiOmitted = api_field(
        description="Read only access to the network scan result", default_factory=ApiOmitted
    )
    meta_data: MetaDataModel | ApiOmitted = api_field(
        description="Read only access to configured metadata.", default_factory=ApiOmitted
    )
