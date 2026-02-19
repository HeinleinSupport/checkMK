load("@aspect_rules_py//py:defs.bzl", "py_binary", "py_library", "py_pytest_main")
load("@bazel_skylib//rules:build_test.bzl", "build_test")
load("@cmk_requirements//:requirements.bzl", "requirement")
load("@rules_python//python:packaging.bzl", "py_wheel")
load("//bazel/rules:doctest.bzl", "py_doc_test")
load("//bazel/rules:package_wheel.bzl", "package_wheel")

exports_files([
    "requirements.in",
    "gui/openapi/spec/spec_generator/generate_api_spec.py",
])

REQUIRED_EXTERNAL_DEPS = [
    # alphabetical order
    "apispec",
    "apispec-oneofschema",
    "azure-identity",
    "azure-storage-blob",
    "bcrypt",
    "boto3",
    "botocore",
    "cryptography",
    "docstring-parser",
    "exchangelib",  # missing wheel
    "fastapi",
    "feedparser",
    "fido2",
    "flask",
    "GitPython",
    "google-api-python-client",
    "google-auth",
    "google-cloud-asset",
    "google-cloud-monitoring",
    "icalendar",
    "jinja2",
    "jira",
    "lxml",
    "markdown",
    "marshmallow",
    "marshmallow-oneofschema",
    "meraki",
    "msal",
    "mypy-boto3-logs",
    "numpy",
    "oauthlib",
    "openapi-spec-validator",
    "opentelemetry-api",
    "opentelemetry-exporter-otlp",
    "opentelemetry-instrumentation-fastapi",
    "opentelemetry-instrumentation-redis",
    "opentelemetry-instrumentation-requests",
    "opentelemetry-instrumentation-wsgi",
    "opentelemetry-sdk",
    "opentelemetry-semantic-conventions",
    "opsgenie-sdk",
    "paho-mqtt",
    "paramiko",
    "pillow",
    "pika",
    "protobuf",
    "psutil",
    "psycopg2-binary",  # missing wheel
    "pyasn1",
    "pydantic",
    "pydantic_core",
    "pyghmi",
    "pyjwt",
    "pymongo",
    "pymssql",
    "pymysql",
    "pyopenssl",
    "pyparsing",
    "pypdf",
    "pyprof2calltree",
    "pysaml2",
    "pysmb",
    "pysmi",
    "pysnmp",
    "python-active-directory",  # missing wheel
    "python-dateutil",
    "python-ldap",  # missing wheel
    "python-multipart",
    "python-snap7",
    "pyyaml",
    "recurring_ical_events",
    "redis",
    "reportlab",
    "requests",
    "requests-oauthlib",
    "robotframework",
    "roman",
    # "rrdtool",
    "setproctitle",
    "setuptools",
    "setuptools-scm",
    "simplejson",
    "snmpsim",
    "tenacity",
    "urllib3",
    "uvicorn",
    "vcrpy",
    "watchdog",
    "werkzeug",
]

filegroup(
    name = "checkman_free",
    srcs = glob(
        [
            "**/checkman/**",
        ],
        exclude = [
            "**/OWNERS",
            "**/checkman/nonfree/**",
        ],
    ),
)

filegroup(
    name = "checkman_edition_specific",
    srcs = select({
        "@cmk//edition:cloud": glob(
            [
                "**/checkman/nonfree/cloud/**",
                "**/checkman/nonfree/ultimate/**",
                "**/checkman/nonfree/pro/**",
            ],
            allow_empty = True,
            exclude = ["**/OWNERS"],
        ),
        "@cmk//edition:community": [],
        "@cmk//edition:pro": glob(
            [
                "**/checkman/nonfree/pro/**",
            ],
            allow_empty = True,
            exclude = ["**/OWNERS"],
        ),
        "@cmk//edition:ultimate": glob(
            [
                "**/checkman/nonfree/ultimate/**",
                "**/checkman/nonfree/pro/**",
            ],
            allow_empty = True,
            exclude = ["**/OWNERS"],
        ),
        "@cmk//edition:ultimatemt": glob(
            [
                "**/checkman/nonfree/ultimatemt/**",
                "**/checkman/nonfree/ultimate/**",
                "**/checkman/nonfree/pro/**",
            ],
            allow_empty = True,
            exclude = ["**/OWNERS"],
        ),
    }),
)

filegroup(
    name = "libexec",
    srcs = glob(
        [
            "**/libexec/*",
        ],
    ),
    visibility = ["//omd:__subpackages__"],
)

filegroup(
    name = "miscellaneous",
    srcs = [
        "gui/wsgi/applications/index.wsgi",
        "//cmk/utils/werks/announce/templates:j2_templates",
    ],
)

filegroup(
    name = "agents",
    srcs = glob(
        include = ["plugins/**/agents/**/*"],
        exclude = ["plugins/**/agents/**/*.py"],
    ),
)

CMK_PACKAGES = [
    "//packages/cmk-shared-typing:cmk_shared_typing_py",
    "//packages/cmk-agent-receiver",
    "//packages/cmk-ccc:cleanup",
    "//packages/cmk-ccc:config-path",
    "//packages/cmk-ccc:cpu-tracking",
    "//packages/cmk-ccc:crash-reporting",
    "//packages/cmk-ccc:daemon",
    "//packages/cmk-ccc:debug",
    "//packages/cmk-ccc:exceptions",
    "//packages/cmk-ccc:hostaddress",
    "//packages/cmk-ccc:i18n",
    "//packages/cmk-ccc:observer",
    "//packages/cmk-ccc:plugin-registry",
    "//packages/cmk-ccc:profile",
    "//packages/cmk-ccc:regex",
    "//packages/cmk-ccc:resulttype",
    "//packages/cmk-ccc:site",
    "//packages/cmk-ccc:store",
    "//packages/cmk-ccc:timeout",
    "//packages/cmk-ccc:translations",
    "//packages/cmk-ccc:tty",
    "//packages/cmk-ccc:user",
    "//packages/cmk-ccc:archive",
    "//packages/cmk-ccc:version",
    "//packages/cmk-check-engine:fetchers",
    "//packages/cmk-check-engine:helper-interface",
    "//packages/cmk-check-engine:snmplib",
    "//packages/cmk-crypto",
    "//packages/cmk-ec",
    "//packages/cmk-events",
    "//packages/cmk-livestatus-client",
    "//packages/cmk-livestatus-client:py_livestatus",
    "//packages/cmk-messaging",
    "//packages/cmk-mkp-tool",
    "//packages/cmk-plugins:lib",
    "//packages/cmk-plugin-apis:agent_based",
    "//packages/cmk-plugin-apis:bakery",
    "//packages/cmk-plugin-apis:discover_plugins",
    "//packages/cmk-plugin-apis:graphing",
    "//packages/cmk-plugin-apis:inventory_ui",
    "//packages/cmk-plugin-apis:rulesets",
    "//packages/cmk-plugin-apis:password_store",
    "//packages/cmk-plugin-apis:server_side_calls",
    "//packages/cmk-plugin-apis:server_side_programs",
    "//packages/cmk-trace",
    "//packages/cmk-werks",
] + select({
    "@//:gpl+nonfree_repo": [
        "//non-free/packages/cmk-core-helpers:check-helper-protocol",
        "//non-free/packages/cmk-core-helpers:fetcher-helper",
        "//non-free/packages/cmk-core-helpers:inline-snmp",
        "//non-free/packages/cmk-metric-backend",
        "//non-free/packages/cmk-mknotifyd",
        "//non-free/packages/cmk-otel-collector",
    ],
    "@//:gpl_repo": [],
})

py_library(
    name = "cmk_cmk",
    srcs = glob(
        include = ["**/*.py"],
        exclude = [
            "**/community/**",
            "**/nonfree/**",
        ],
    ),
    data = ["gui/wsgi/applications/index.wsgi"],
    imports = [".."],
    visibility = ["//:__subpackages__"],
    deps = [
        "//cmk/utils:cmk_utils",
        "@rrdtool_native//:rrdtool_python_lib",
    ] + CMK_PACKAGES + [requirement(dep) for dep in REQUIRED_EXTERNAL_DEPS],
)

py_library(
    name = "cmk_community",
    srcs = glob(
        include = ["**/community/**/*.py"],
        allow_empty = True,
        exclude = ["**/nonfree/**"],
    ),
    imports = [".."],
    visibility = ["//:__subpackages__"],
    deps = [":cmk_cmk"] + [requirement(dep) for dep in REQUIRED_EXTERNAL_DEPS],
)

py_library(
    name = "cmk_pro",
    srcs = glob(
        include = [
            "**/nonfree/**/pro/**/*.py",
            "**/nonfree/**/*.py",
        ],
        allow_empty = True,
        exclude = [
            "**/nonfree/**/cloud/**",
            "**/nonfree/**/ultimate/**",
            "**/nonfree/**/ultimatemt/**",
        ],
    ),
    imports = [".."],
    visibility = ["//:__subpackages__"],
    deps = [
        ":cmk_cmk",
        ":cmk_community",
        "//cmk/utils:cmk_utils_pro",
    ] + select({
        "@//:gpl+nonfree_repo": [
            "//non-free/packages/cmc-protocols:py_config_proto",
            "//non-free/packages/cmc-protocols:py_cycletime_proto",
            "//non-free/packages/cmc-protocols:py_state_proto",
            "//non-free/packages/cmk-core-helpers:relay-fetcher-trigger",
            "//non-free/packages/cmk-metric-backend",
            "//non-free/packages/cmk-mknotifyd",
            "//non-free/packages/cmk-otel-collector",
            "//non-free/packages/cmk-update-agent:cmk-update-agent-py",
        ],
        "@//:gpl_repo": [],
    }) + [requirement(dep) for dep in REQUIRED_EXTERNAL_DEPS],
)

py_library(
    name = "cmk_ultimate",
    srcs = glob(
        include = ["**/nonfree/**/ultimate/**/*.py"],
        allow_empty = True,
    ),
    imports = [".."],
    visibility = ["//:__subpackages__"],
    deps = [
        ":cmk_cmk",
        ":cmk_community",
        ":cmk_pro",
        "//cmk/utils:cmk_utils_ultimate",
    ] + select({
        "@//:gpl+nonfree_repo": [
            "//non-free/packages/cmc-protocols:py_config_proto",
            "//non-free/packages/cmc-protocols:py_cycletime_proto",
            "//non-free/packages/cmc-protocols:py_state_proto",
        ],
        "@//:gpl_repo": [],
    }) + [requirement(dep) for dep in REQUIRED_EXTERNAL_DEPS],
)

py_library(
    name = "cmk_cloud",
    srcs = glob(
        include = ["**/nonfree/**/cloud/**/*.py"],
        allow_empty = True,
    ),
    imports = [".."],
    visibility = ["//:__subpackages__"],
    deps = [
        ":cmk_cmk",
        ":cmk_community",
        ":cmk_pro",
        ":cmk_ultimate",
        "//cmk/utils:cmk_utils_cloud",
    ] + select({
        "@//:gpl+nonfree_repo": [
            "//non-free/packages/cmc-protocols:py_config_proto",
            "//non-free/packages/cmc-protocols:py_cycletime_proto",
            "//non-free/packages/cmc-protocols:py_state_proto",
            "//non-free/packages/cmk-core-helpers:relay-fetcher-trigger",
            "//non-free/packages/cmk-metric-backend",
            "//non-free/packages/cmk-mknotifyd",
            "//non-free/packages/cmk-otel-collector",
            "//non-free/packages/cmk-update-agent:cmk-update-agent-py",
        ],
        "@//:gpl_repo": [],
    }) + [requirement(dep) for dep in REQUIRED_EXTERNAL_DEPS],
)

py_library(
    name = "cmk_ultimatemt",
    srcs = glob(
        include = ["**/nonfree/**/ultimatemt/**/*.py"],
        allow_empty = True,
    ),
    imports = [".."],
    visibility = ["//:__subpackages__"],
    deps = [
        ":cmk_cmk",
        ":cmk_community",
        ":cmk_pro",
        ":cmk_ultimate",
        "//cmk/utils:cmk_utils_ultimatemt",
    ] + select({
        "@//:gpl+nonfree_repo": [
            "//non-free/packages/cmc-protocols:py_config_proto",
            "//non-free/packages/cmc-protocols:py_cycletime_proto",
            "//non-free/packages/cmc-protocols:py_state_proto",
            "//non-free/packages/cmk-core-helpers:relay-fetcher-trigger",
            "//non-free/packages/cmk-metric-backend",
            "//non-free/packages/cmk-mknotifyd",
            "//non-free/packages/cmk-otel-collector",
            "//non-free/packages/cmk-update-agent:cmk-update-agent-py",
        ],
        "@//:gpl_repo": [],
    }) + [requirement(dep) for dep in REQUIRED_EXTERNAL_DEPS],
)

py_wheel(
    name = "cmk_whl",
    distribution = "checkmk",
    requires = REQUIRED_EXTERNAL_DEPS,
    # TODO(ml): cmk_version vs. PEP 440?
    version = "1+" + select({
        "@cmk//edition:cloud": "cloud",
        "@cmk//edition:community": "community",
        "@cmk//edition:pro": "pro",
        "@cmk//edition:ultimate": "ultimate",
        "@cmk//edition:ultimatemt": "ultimatemt",
    }),
    visibility = ["//visibility:public"],
    deps = select({
        "@cmk//edition:cloud": [
            ":cmk_cloud",
            ":cmk_community",
            ":cmk_pro",
            ":cmk_ultimate",
            "//cmk/utils:cmk_utils_cloud",
            "//cmk/utils:cmk_utils_pro",
            "//non-free/packages/cmc-protocols:py_config_proto",
            "//non-free/packages/cmc-protocols:py_cycletime_proto",
            "//non-free/packages/cmc-protocols:py_state_proto",
        ],
        "@cmk//edition:community": [
            ":cmk_community",
            "//cmk/utils:cmk_utils_community",
        ],
        "@cmk//edition:pro": [
            ":cmk_community",
            ":cmk_pro",
            "//cmk/utils:cmk_utils_pro",
            "//non-free/packages/cmc-protocols:py_config_proto",
            "//non-free/packages/cmc-protocols:py_cycletime_proto",
            "//non-free/packages/cmc-protocols:py_state_proto",
        ],
        "@cmk//edition:ultimate": [
            ":cmk_community",
            ":cmk_pro",
            ":cmk_ultimate",
            "//cmk/utils:cmk_utils_pro",
            "//cmk/utils:cmk_utils_ultimate",
            "//non-free/packages/cmc-protocols:py_config_proto",
            "//non-free/packages/cmc-protocols:py_cycletime_proto",
            "//non-free/packages/cmc-protocols:py_state_proto",
        ],
        "@cmk//edition:ultimatemt": [
            ":cmk_community",
            ":cmk_pro",
            ":cmk_ultimate",
            ":cmk_ultimatemt",
            "//cmk/utils:cmk_utils_pro",
            "//cmk/utils:cmk_utils_ultimate",
            "//cmk/utils:cmk_utils_ultimatemt",
            "//non-free/packages/cmc-protocols:py_config_proto",
            "//non-free/packages/cmc-protocols:py_cycletime_proto",
            "//non-free/packages/cmc-protocols:py_state_proto",
        ],
    }) + [
        ":agents",
        ":checkman_edition_specific",
        ":checkman_free",
        ":cmk_cmk",
        ":miscellaneous",
        "//cmk/utils:cmk_utils",
    ],
)

build_test(
    name = "build_test",
    targets = ["cmk_whl"],
)

package_wheel(
    name = "cmk_tar",
    prefix = "lib/python3",
    visibility = ["//visibility:public"],
    whl = "cmk_whl",
)

py_pytest_main(
    name = "__test__",
    deps = [
        requirement("pytest"),
        # pytest-xdist for `--numprocesses=NPROC`
        requirement("pytest-xdist"),
    ],
)

py_doc_test(
    name = "doctest",
    srcs = [
        ":cmk_cloud",
        ":cmk_cmk",
        ":cmk_community",
        ":cmk_pro",
        ":cmk_ultimate",
        ":cmk_ultimatemt",
    ],
    env = {
        "PYTHONWARNINGS": "ignore",
    },
    tags = ["no-mypy"],
)

py_binary(
    name = "generate_api_spec",
    srcs = ["gui/openapi/spec/spec_generator/generate_api_spec.py"],
    main = "gui/openapi/spec/spec_generator/generate_api_spec.py",
    visibility = ["//:__subpackages__"],
    deps = [
        ":cmk_cloud",
        ":cmk_community",
        ":cmk_pro",
        ":cmk_ultimate",
        ":cmk_ultimatemt",
        requirement("pyyaml"),
    ],
)

sh_library(
    name = "cmk_sh",
    srcs = [
        ".f12",
        "base/.f12",
        "config_anonymizer/.f12",
        "gui/.f12",
        "gui/openapi/.f12",
        "gui/wsgi/.f12",
        "plugins/activemq/libexec/agent_activemq",
        "plugins/alertmanager/libexec/agent_alertmanager",
        "plugins/allnet_ip_sensoric/libexec/agent_allnet_ip_sensoric",
        "plugins/appdynamics/libexec/agent_appdynamics",
        "plugins/aws/libexec/agent_aws",
        "plugins/aws/libexec/agent_aws_status",
        "plugins/azure_deprecated/libexec/agent_azure",
        "plugins/azure_status/libexec/agent_azure_status",
        "plugins/azure_v2/libexec/agent_azure_v2",
        "plugins/bazel/libexec/agent_bazel_cache",
        "plugins/checkmk/libexec/agent_bi",
        "plugins/checkmk/libexec/check_bi_aggr",
        "plugins/checkmk/libexec/check_cmk_inv",
        "plugins/cisco_meraki/libexec/agent_cisco_meraki",
        "plugins/couchbase/libexec/agent_couchbase",
        "plugins/datadog/libexec/agent_datadog",
        "plugins/ddn_s2a/libexec/agent_ddn_s2a",
        "plugins/emailchecks/libexec/check_mail",
        "plugins/emailchecks/libexec/check_mail_loop",
        "plugins/emailchecks/libexec/check_mailboxes",
        "plugins/form_submit/libexec/check_form_submit",
        "plugins/fritzbox/libexec/agent_fritzbox",
        "plugins/gcp/libexec/agent_gcp",
        "plugins/gcp/libexec/agent_gcp_status",
        "plugins/gerrit/libexec/agent_gerrit",
        "plugins/graylog/libexec/agent_graylog",
        "plugins/hivemanager/libexec/agent_hivemanager",
        "plugins/hivemanager_ng/libexec/agent_hivemanager_ng",
        "plugins/hp_msa/libexec/agent_hp_msa",
        "plugins/hpe_3par/libexec/agent_three_par",
        "plugins/ibmsvc/libexec/agent_ibmsvc",
        "plugins/innovaphone/libexec/agent_innovaphone",
        "plugins/jenkins/libexec/agent_jenkins",
        "plugins/jira/libexec/agent_jira",
        "plugins/jolokia/libexec/agent_jolokia",
        "plugins/mobileiron/libexec/agent_mobileiron",
        "plugins/mqtt/libexec/agent_mqtt",
        "plugins/oracle/.f12",
        "plugins/oracle/agents/oracle_unified_async",
        "plugins/oracle/agents/oracle_unified_sync",
        "plugins/prometheus/libexec/agent_prometheus",
        "plugins/ruckus_spot/libexec/agent_ruckus_spot",
        "plugins/salesforce/libexec/agent_salesforce",
        "plugins/sftp/libexec/check_sftp",
        "plugins/siemens_plc/libexec/agent_siemens_plc",
        "plugins/smb/libexec/agent_smb_share",
        "plugins/smb/libexec/check_disk_smb",
        "plugins/sql/libexec/check_sql",
        "plugins/storeonce/libexec/agent_storeonce",
        "plugins/storeonce4x/libexec/agent_storeonce4x",
        "plugins/tinkerforge/libexec/agent_tinkerforge",
        "plugins/traceroute/libexec/check_traceroute",
        "plugins/uniserv/libexec/check_uniserv",
        "plugins/vnx_quotas/libexec/agent_vnx_quotas",
        "plugins/zerto/libexec/agent_zerto",
    ] + select({
        "@//:gpl+nonfree_repo": [
            "gui/nonfree/pro/dcd/.f12",
            "nonfree/pro/dcd/.f12",
            "nonfree/pro/robotmk/.f12",
            "//cmk/utils:nonfree/pro/dcd/.f12",
        ],
        "@//:gpl_repo": [],
    }),
)
