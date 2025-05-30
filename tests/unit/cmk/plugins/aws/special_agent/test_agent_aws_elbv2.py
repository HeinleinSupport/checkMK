#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


from argparse import Namespace as Args
from collections.abc import Sequence
from typing import NamedTuple, Protocol

import pytest

from cmk.plugins.aws.special_agent.agent_aws import (
    AWSConfig,
    ELBLabelsGeneric,
    ELBSummaryGeneric,
    ELBv2Application,
    ELBv2ApplicationTargetGroupsHTTP,
    ELBv2ApplicationTargetGroupsLambda,
    ELBv2Limits,
    ELBv2Network,
    ELBv2TargetGroups,
    NamingConvention,
    OverallTags,
    ResultDistributor,
    TagsImportPatternOption,
    TagsOption,
)

from .agent_aws_fake_clients import (
    ELBDescribeTagsIB,
    ELBv2DescribeAccountLimitsIB,
    ELBv2DescribeListenersIB,
    ELBv2DescribeLoadBalancersIB,
    ELBv2DescribeRulesIB,
    ELBv2DescribeTargetGroupsIB,
    ELBv2DescribeTargetHealthIB,
    FakeCloudwatchClient,
)


class Paginator:
    def paginate(self, Names=None):
        load_balancers = ELBv2DescribeLoadBalancersIB.create_instances(amount=3)
        if Names is not None:
            load_balancers = [
                load_balancer
                for load_balancer in load_balancers
                if load_balancer["LoadBalancerName"] in Names
            ]
        yield {
            "LoadBalancers": load_balancers,
            "NextMarker": "string",
        }


class FakeELBv2Client:
    def describe_tags(self, ResourceArns=None):
        lbs = ELBDescribeTagsIB.create_instances(amount=3)  # 3 needed to get more than one tag each
        tagged_lbs = set(ResourceArns or []).intersection(
            {"LoadBalancerArn-0", "LoadBalancerArn-1"}
        )
        return {"TagDescriptions": [lb for lb in lbs if lb["LoadBalancerArn"] in tagged_lbs]}

    def describe_target_groups(self, LoadBalancerArn=None):
        return {
            "TargetGroups": ELBv2DescribeTargetGroupsIB.create_instances(amount=1),
            "NextMarker": "string",
        }

    def describe_listeners(self, LoadBalancerArn=None):
        return {
            "Listeners": ELBv2DescribeListenersIB.create_instances(amount=1),
            "NextMarker": "string",
        }

    def describe_rules(self, ListenerArn=None):
        return {
            "Rules": ELBv2DescribeRulesIB.create_instances(amount=1),
            "NextMarker": "string",
        }

    def describe_account_limits(self):
        return {
            "Limits": ELBv2DescribeAccountLimitsIB.create_instances(amount=1)[0]["Limits"],
            "NextMarker": "string",
        }

    def describe_target_health(self, TargetGroupArn=None):
        return {
            "TargetHealthDescriptions": ELBv2DescribeTargetHealthIB.create_instances(amount=1),
        }

    def get_paginator(self, operation_name):
        if operation_name == "describe_load_balancers":
            return Paginator()
        raise NotImplementedError


class ELBv2SectionsOut(NamedTuple):
    elbv2_limits: ELBv2Limits
    elbv2_summary: ELBSummaryGeneric
    elbv2_labels: ELBLabelsGeneric
    elbv2_target_groups: ELBv2TargetGroups
    elbv2_application: tuple[
        ELBv2Application, ELBv2ApplicationTargetGroupsHTTP, ELBv2ApplicationTargetGroupsLambda
    ]
    elbv2_network: ELBv2Network


class ELBv2Sections(Protocol):
    def __call__(
        self,
        names: object | None = None,
        tags: OverallTags = (None, None),
        tag_import: TagsOption = TagsImportPatternOption.import_all,
    ) -> ELBv2SectionsOut: ...


@pytest.fixture()
def get_elbv2_sections() -> ELBv2Sections:
    def _create_elbv2_sections(
        names: object | None = None,
        tags: OverallTags = (None, None),
        tag_import: TagsOption = TagsImportPatternOption.import_all,
    ) -> ELBv2SectionsOut:
        region = "region"
        config = AWSConfig(
            "hostname", Args(), ([], []), NamingConvention.ip_region_instance, tag_import
        )
        config.add_single_service_config("elbv2_names", names)
        config.add_service_tags("elbv2_tags", tags)

        fake_elbv2_client = FakeELBv2Client()
        fake_cloudwatch_client = FakeCloudwatchClient()

        distributor = ResultDistributor()

        # TODO: FakeELBv2Client shoud actually subclass ELBv2Client, etc.
        elbv2_limits = ELBv2Limits(fake_elbv2_client, region, config, distributor)  # type: ignore[arg-type]
        elbv2_summary = ELBSummaryGeneric(
            fake_elbv2_client,  # type: ignore[arg-type]
            region,
            config,
            distributor,
            resource="elbv2",
        )
        elbv2_labels = ELBLabelsGeneric(fake_elbv2_client, region, config, resource="elbv2")  # type: ignore[arg-type]
        elbv2_target_groups = ELBv2TargetGroups(fake_elbv2_client, region, config)  # type: ignore[arg-type]
        elbv2_application = ELBv2Application(fake_cloudwatch_client, region, config)  # type: ignore[arg-type]
        elbv2_application_target_groups_http = ELBv2ApplicationTargetGroupsHTTP(
            fake_cloudwatch_client,  # type: ignore[arg-type]
            region,
            config,
        )
        elbv2_application_target_groups_lambda = ELBv2ApplicationTargetGroupsLambda(
            fake_cloudwatch_client,  # type: ignore[arg-type]
            region,
            config,
        )
        elbv2_network = ELBv2Network(fake_cloudwatch_client, region, config)  # type: ignore[arg-type]

        distributor.add(elbv2_limits.name, elbv2_summary)
        distributor.add(elbv2_summary.name, elbv2_labels)
        distributor.add(elbv2_summary.name, elbv2_target_groups)
        distributor.add(elbv2_summary.name, elbv2_application)
        distributor.add(elbv2_summary.name, elbv2_application_target_groups_http)
        distributor.add(elbv2_summary.name, elbv2_application_target_groups_lambda)
        distributor.add(elbv2_summary.name, elbv2_network)

        return ELBv2SectionsOut(
            elbv2_limits=elbv2_limits,
            elbv2_summary=elbv2_summary,
            elbv2_labels=elbv2_labels,
            elbv2_target_groups=elbv2_target_groups,
            elbv2_application=(
                elbv2_application,
                elbv2_application_target_groups_http,
                elbv2_application_target_groups_lambda,
            ),
            elbv2_network=elbv2_network,
        )

    return _create_elbv2_sections


def check_target_groups_results(
    piggyback_hostname, target_group_name, target_groups_results, expected_length
):
    for result in target_groups_results:
        entry_found = result.piggyback_hostname == piggyback_hostname

        if entry_found:
            for metric in result.content:
                entry_found &= metric["Label"] == target_group_name

        if entry_found:
            assert len(result.content) == expected_length
            break


def check_target_group_errors_results(
    elbv2_summary_content,
    elbv2_application_target_groups_http_results,
    elbv2_application_target_groups_lambda_results,
):
    n_elbv2_application = 0
    n_tg_lambda = 0
    n_tg_instance_ip = 0

    for elbv2 in elbv2_summary_content:
        if elbv2["Type"] == "application":
            n_elbv2_application += 1
            piggyback_hostname = elbv2["DNSName"]

            for target_group in elbv2["TargetGroups"]:
                if target_group["TargetType"] == "lambda":
                    n_tg_lambda += 1
                    check_target_groups_results(
                        piggyback_hostname,
                        target_group["TargetGroupName"],
                        elbv2_application_target_groups_lambda_results,
                        2,
                    )

                else:
                    n_tg_instance_ip += 1
                    check_target_groups_results(
                        piggyback_hostname,
                        target_group["TargetGroupName"],
                        elbv2_application_target_groups_http_results,
                        5,
                    )

    n_metrics_instance_ip = 0
    for result in elbv2_application_target_groups_http_results:
        n_metrics_instance_ip += len(result.content)

    n_metrics_lambda = 0
    for result in elbv2_application_target_groups_lambda_results:
        n_metrics_lambda += len(result.content)

    assert n_elbv2_application == len(elbv2_application_target_groups_http_results) + len(
        elbv2_application_target_groups_lambda_results
    )
    assert n_metrics_instance_ip == 5 * n_tg_instance_ip  # 5 metrics per target group
    assert n_metrics_lambda == 2 * n_tg_lambda  # 2 metrics per target group


elbv2_params = [
    (
        None,
        (None, None),
        ["LoadBalancerName-0", "LoadBalancerName-1", "LoadBalancerName-2"],
        ["LoadBalancerName-0", "LoadBalancerName-1"],
    ),
    (None, ([["FOO"]], [["BAR"]]), [], []),
    (
        None,
        ([["Key-0"]], [["Value-0"]]),
        ["LoadBalancerName-0", "LoadBalancerName-1"],
        ["LoadBalancerName-0", "LoadBalancerName-1"],
    ),
    (
        None,
        ([["Key-0", "Foo"]], [["Value-0", "Bar"]]),
        ["LoadBalancerName-0", "LoadBalancerName-1"],
        ["LoadBalancerName-0", "LoadBalancerName-1"],
    ),
    (["LoadBalancerName-0"], (None, None), ["LoadBalancerName-0"], ["LoadBalancerName-0"]),
    (
        ["LoadBalancerName-0", "Foobar"],
        (None, None),
        ["LoadBalancerName-0"],
        ["LoadBalancerName-0"],
    ),
    (
        ["LoadBalancerName-0", "LoadBalancerName-1"],
        (None, None),
        ["LoadBalancerName-0", "LoadBalancerName-1"],
        ["LoadBalancerName-0", "LoadBalancerName-1"],
    ),
    (
        ["LoadBalancerName-0", "LoadBalancerName-2"],
        (None, None),
        ["LoadBalancerName-0", "LoadBalancerName-2"],
        ["LoadBalancerName-0"],
    ),
    (["LoadBalancerName-2"], ([["FOO"]], [["BAR"]]), ["LoadBalancerName-2"], []),
]


@pytest.mark.parametrize("names,tags,found_instances,found_instances_with_labels", elbv2_params)
def test_agent_aws_elbv2_limits(
    get_elbv2_sections: ELBv2Sections,
    names: Sequence[str] | None,
    tags: OverallTags,
    found_instances: Sequence[str],
    found_instances_with_labels: Sequence[str],
) -> None:
    elbv2_limits = get_elbv2_sections(names, tags).elbv2_limits
    elbv2_limits_results = elbv2_limits.run().results

    assert elbv2_limits.cache_interval == 300
    assert elbv2_limits.period == 600
    assert elbv2_limits.name == "elbv2_limits"
    assert len(elbv2_limits_results) == 4
    for result in elbv2_limits_results:
        if result.piggyback_hostname == "":
            assert len(result.content) == 3
        else:
            # Dependent on load balancer type "application" or "network" we have 2 or 4 limits
            assert len(result.content) in (2, 4)


@pytest.mark.parametrize("names,tags,found_instances,found_instances_with_labels", elbv2_params)
def test_agent_aws_elbv2_summary(
    get_elbv2_sections: ELBv2Sections,
    names: Sequence[str] | None,
    tags: OverallTags,
    found_instances: Sequence[str],
    found_instances_with_labels: Sequence[str],
) -> None:
    elbv2_sections = get_elbv2_sections(names, tags)
    elbv2_summary = elbv2_sections.elbv2_summary
    elbv2_sections.elbv2_limits.run()
    elbv2_summary_results = elbv2_summary.run().results

    assert elbv2_summary.cache_interval == 300
    assert elbv2_summary.period == 600
    assert elbv2_summary.name == "elbv2_summary"

    if found_instances:
        assert len(elbv2_summary_results) == 1
        elbv2_summary_result = elbv2_summary_results[0]
        assert elbv2_summary_result.piggyback_hostname == ""
        assert len(elbv2_summary_result.content) == len(found_instances)

    else:
        assert len(elbv2_summary_results) == 0


@pytest.mark.parametrize("names,tags,found_instances,found_instances_with_labels", elbv2_params)
def test_agent_aws_elbv2_labels(
    get_elbv2_sections: ELBv2Sections,
    names: Sequence[str] | None,
    tags: OverallTags,
    found_instances: Sequence[str],
    found_instances_with_labels: Sequence[str],
) -> None:
    elbv2_sections = get_elbv2_sections(names, tags)
    elbv2_sections.elbv2_limits.run()
    elbv2_sections.elbv2_summary.run()
    elbv2_labels = elbv2_sections.elbv2_labels
    elbv2_labels_results = elbv2_labels.run().results

    assert elbv2_labels.cache_interval == 300
    assert elbv2_labels.period == 600
    assert elbv2_labels.name == "elbv2_generic_labels"
    assert len(elbv2_labels_results) == len(found_instances_with_labels)
    for result in elbv2_labels_results:
        assert result.piggyback_hostname != ""


@pytest.mark.parametrize("names,tags,found_instances,found_instances_with_labels", elbv2_params)
def test_agent_aws_elbv2_target_groups(
    get_elbv2_sections: ELBv2Sections,
    names: Sequence[str] | None,
    tags: OverallTags,
    found_instances: Sequence[str],
    found_instances_with_labels: Sequence[str],
) -> None:
    elbv2_sections = get_elbv2_sections(names, tags)
    elbv2_sections.elbv2_limits.run()
    elbv2_sections.elbv2_summary.run()
    elbv2_target_groups = elbv2_sections.elbv2_target_groups
    elbv2_target_groups_results = elbv2_target_groups.run().results

    assert elbv2_target_groups.cache_interval == 300
    assert elbv2_target_groups.period == 600
    assert elbv2_target_groups.name == "elbv2_target_groups"
    assert len(elbv2_target_groups_results) == len(found_instances)
    for result in elbv2_target_groups_results:
        assert result.piggyback_hostname != ""


@pytest.mark.parametrize("names,tags,found_instances,found_instances_with_labels", elbv2_params)
def test_agent_aws_elbv2_application(
    get_elbv2_sections: ELBv2Sections,
    names: Sequence[str] | None,
    tags: OverallTags,
    found_instances: Sequence[str],
    found_instances_with_labels: Sequence[str],
) -> None:
    elbv2_sections = get_elbv2_sections(names, tags)
    elbv2_sections.elbv2_limits.run()
    elbv2_summary_results = elbv2_sections.elbv2_summary.run().results
    (
        elbv2_application,
        elbv2_application_target_groups_http,
        elbv2_application_target_groups_lambda,
    ) = elbv2_sections.elbv2_application
    elbv2_application_results = elbv2_application.run().results
    elbv2_application_target_groups_http_results = (
        elbv2_application_target_groups_http.run().results
    )
    elbv2_application_target_groups_lambda_results = (
        elbv2_application_target_groups_lambda.run().results
    )

    assert elbv2_application.cache_interval == 300
    assert elbv2_application.period == 600
    assert elbv2_application.name == "elbv2_application"
    assert len(elbv2_application_results) == len(found_instances)
    for result in elbv2_application_results:
        assert result.piggyback_hostname != ""
        # 20 metrics
        assert len(result.content) == 20

    assert elbv2_application_target_groups_http.cache_interval == 300
    assert elbv2_application_target_groups_http.period == 600
    assert elbv2_application_target_groups_lambda.cache_interval == 300
    assert elbv2_application_target_groups_lambda.period == 600
    assert elbv2_application_target_groups_http.name == "elbv2_application_target_groups_http"
    assert elbv2_application_target_groups_lambda.name == "elbv2_application_target_groups_lambda"

    if len(found_instances) > 0:
        check_target_group_errors_results(
            elbv2_summary_results[0].content,
            elbv2_application_target_groups_http_results,
            elbv2_application_target_groups_lambda_results,
        )


@pytest.mark.parametrize("names,tags,found_instances,found_instances_with_labels", elbv2_params)
def test_agent_aws_elbv2_network(
    get_elbv2_sections: ELBv2Sections,
    names: Sequence[str] | None,
    tags: OverallTags,
    found_instances: Sequence[str],
    found_instances_with_labels: Sequence[str],
) -> None:
    elbv2_sections = get_elbv2_sections(names, tags)
    elbv2_sections.elbv2_limits.run()
    elbv2_sections.elbv2_summary.run()
    elbv2_network = elbv2_sections.elbv2_network
    elbv2_network_results = elbv2_network.run().results

    assert elbv2_network.cache_interval == 300
    assert elbv2_network.period == 600
    assert elbv2_network.name == "elbv2_network"
    assert len(elbv2_network_results) == len(found_instances)
    for result in elbv2_network_results:
        assert result.piggyback_hostname != ""
        # 12 metrics
        assert len(result.content) == 12


@pytest.mark.parametrize("names,tags,found_instances,found_instances_with_labels", elbv2_params)
def test_agent_aws_elbv2_summary_without_limits(
    get_elbv2_sections: ELBv2Sections,
    names: Sequence[str] | None,
    tags: OverallTags,
    found_instances: Sequence[str],
    found_instances_with_labels: Sequence[str],
) -> None:
    elbv2_sections = get_elbv2_sections(names, tags)
    elbv2_summary = elbv2_sections.elbv2_summary
    elbv2_summary_results = elbv2_summary.run().results

    assert elbv2_summary.cache_interval == 300
    assert elbv2_summary.period == 600
    assert elbv2_summary.name == "elbv2_summary"

    if found_instances:
        assert len(elbv2_summary_results) == 1
        elbv2_summary_result = elbv2_summary_results[0]
        assert elbv2_summary_result.piggyback_hostname == ""
        assert len(elbv2_summary_result.content) == len(found_instances)

    else:
        assert len(elbv2_summary_results) == 0


@pytest.mark.parametrize("names,tags,found_instances,found_instances_with_labels", elbv2_params)
def test_agent_aws_elbv2_labels_without_limits(
    get_elbv2_sections: ELBv2Sections,
    names: Sequence[str] | None,
    tags: OverallTags,
    found_instances: Sequence[str],
    found_instances_with_labels: Sequence[str],
) -> None:
    elbv2_sections = get_elbv2_sections(names, tags)
    elbv2_sections.elbv2_summary.run()
    elbv2_labels = elbv2_sections.elbv2_labels
    elbv2_labels_results = elbv2_labels.run().results

    assert elbv2_labels.cache_interval == 300
    assert elbv2_labels.period == 600
    assert elbv2_labels.name == "elbv2_generic_labels"
    assert len(elbv2_labels_results) == len(found_instances_with_labels)
    for result in elbv2_labels_results:
        assert result.piggyback_hostname != ""


@pytest.mark.parametrize("names,tags,found_instances,found_instances_with_labels", elbv2_params)
def test_agent_aws_elbv2_target_groups_without_limits(
    get_elbv2_sections: ELBv2Sections,
    names: Sequence[str] | None,
    tags: OverallTags,
    found_instances: Sequence[str],
    found_instances_with_labels: Sequence[str],
) -> None:
    elbv2_sections = get_elbv2_sections(names, tags)
    elbv2_sections.elbv2_summary.run()
    elbv2_target_groups = elbv2_sections.elbv2_target_groups
    elbv2_target_groups_results = elbv2_target_groups.run().results

    assert elbv2_target_groups.cache_interval == 300
    assert elbv2_target_groups.period == 600
    assert elbv2_target_groups.name == "elbv2_target_groups"
    assert len(elbv2_target_groups_results) == len(found_instances)
    for result in elbv2_target_groups_results:
        assert result.piggyback_hostname != ""


@pytest.mark.parametrize("names,tags,found_instances,found_instances_with_labels", elbv2_params)
def test_agent_aws_elbv2_application_without_limits(
    get_elbv2_sections: ELBv2Sections,
    names: Sequence[str] | None,
    tags: OverallTags,
    found_instances: Sequence[str],
    found_instances_with_labels: Sequence[str],
) -> None:
    elbv2_sections = get_elbv2_sections(names, tags)
    elbv2_summary_results = elbv2_sections.elbv2_summary.run().results
    elbv2_sections.elbv2_target_groups.run()
    (
        elbv2_application,
        elbv2_application_target_groups_http,
        elbv2_application_target_groups_lambda,
    ) = elbv2_sections.elbv2_application
    elbv2_application_results = elbv2_application.run().results
    elbv2_application_target_groups_http_results = (
        elbv2_application_target_groups_http.run().results
    )
    elbv2_application_target_groups_lambda_results = (
        elbv2_application_target_groups_lambda.run().results
    )

    assert elbv2_application.cache_interval == 300
    assert elbv2_application.period == 600
    assert elbv2_application.name == "elbv2_application"
    assert len(elbv2_application_results) == len(found_instances)
    for result in elbv2_application_results:
        assert result.piggyback_hostname != ""
        # 20 metrics
        assert len(result.content) == 20

    assert elbv2_application_target_groups_http.cache_interval == 300
    assert elbv2_application_target_groups_http.period == 600
    assert elbv2_application_target_groups_lambda.cache_interval == 300
    assert elbv2_application_target_groups_lambda.period == 600
    assert elbv2_application_target_groups_http.name == "elbv2_application_target_groups_http"
    assert elbv2_application_target_groups_lambda.name == "elbv2_application_target_groups_lambda"

    if len(found_instances) > 0:
        check_target_group_errors_results(
            elbv2_summary_results[0].content,
            elbv2_application_target_groups_http_results,
            elbv2_application_target_groups_lambda_results,
        )


@pytest.mark.parametrize("names,tags,found_instances,found_instances_with_labels", elbv2_params)
def test_agent_aws_elbv2_network_without_limits(
    get_elbv2_sections: ELBv2Sections,
    names: Sequence[str] | None,
    tags: OverallTags,
    found_instances: Sequence[str],
    found_instances_with_labels: Sequence[str],
) -> None:
    elbv2_sections = get_elbv2_sections(names, tags)
    elbv2_sections.elbv2_summary.run()
    elbv2_network = elbv2_sections.elbv2_network
    elbv2_network_results = elbv2_network.run().results

    assert elbv2_network.cache_interval == 300
    assert elbv2_network.period == 600
    assert elbv2_network.name == "elbv2_network"
    assert len(elbv2_network_results) == len(found_instances)
    for result in elbv2_network_results:
        assert result.piggyback_hostname != ""
        # 12 metrics
        assert len(result.content) == 12


@pytest.mark.parametrize(
    "tag_import, expected_tags",
    [
        (TagsImportPatternOption.import_all, ["Key-0", "Key-1", "Key-2"]),
        (r".*-1$", ["Key-1"]),
        (TagsImportPatternOption.ignore_all, []),
    ],
)
def test_agent_aws_elbv2_filters_tags(
    get_elbv2_sections: ELBv2Sections,
    tag_import: TagsOption,
    expected_tags: Sequence[str],
) -> None:
    sections = get_elbv2_sections(tag_import=tag_import)
    elb_summary_results = sections.elbv2_summary.run().results
    elb_labels_results = sections.elbv2_labels.run().results

    if expected_tags:
        labels_row = elb_labels_results[0].content
        assert list(labels_row.keys()) == expected_tags
    else:
        assert len(elb_labels_results) == 0

    for result in elb_summary_results:
        assert list(result.content[0]["TagsForCmkLabels"].keys()) == expected_tags
