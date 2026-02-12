load("@aspect_rules_py//py:defs.bzl", "py_library", "py_pytest_main", "py_test")
load("@bazel_skylib//rules:write_file.bzl", "write_file")
load("@cmk_requirements//:requirements.bzl", "requirement")

package(default_visibility = [":__subpackages__"])

py_library(
    name = "conftest",
    testonly = True,
    srcs = [
        "conftest.py",
        "mocks_and_helpers.py",
    ],
    deps = [
        "//cmk:cmk_cmk",
        "//packages/cmk-livestatus-client:py_livestatus",
        "//tests:testlib",
        requirement("fakeredis"),
        requirement("pytest_metadata"),
    ],
)

py_pytest_main(
    name = "__test__",
    deps = [
        requirement("pytest"),
        # pytest-xdist for `--numprocesses=NPROC`
        requirement("pytest-xdist"),
    ],
)

write_file(
    name = "cannot_fail",
    out = "test_cannot_fail.py",
    content = [
        "def test_cannot_fail() -> None:",
        "    assert True",
    ],
)

py_test(
    # Start the collection and load the conftests.  The complexity
    # of those warrants this target.
    name = "smoke",
    size = "small",
    srcs = [
        "__test__.py",
        "test_cannot_fail.py",
    ],
    args = [
        "--config-file=$(location @//:pyproject.toml)",
        "--import-mode=importlib",
    ],
    data = ["@//:pyproject.toml"],
    main = ":__test__.py",
    deps = [
        ":__test__",
        ":conftest",
        "//cmk:cmk_cmk",
        "//tests:testlib",
    ],
)

py_test(
    name = "omdlib_unit",
    srcs = ["__test__.py"] + glob(
        include = ["omdlib/*.py"],
    ),
    args = [
        "--config-file=$(location @//:pyproject.toml)",
        "--import-mode=importlib",
    ],
    data = ["@//:pyproject.toml"],
    main = ":__test__.py",
    deps = [
        ":__test__",
        "//omd/packages/omd:omdlib",
        requirement("pytest-mock"),
        requirement("cryptography"),
    ],
)

py_test(
    name = "repo",
    # https://bazel.build/reference/be/common-definitions#test.size
    size = "large",
    srcs = ["__test__.py"] + glob(
        include = ["**/*.py"],
        exclude = [
            "omdlib/**/*.py",
            "cmk/gui/nonfree/pro/agent_bakery/test_bake_agents.py",
            "cmk/gui/nonfree/pro/agent_bakery/test_misc.py",
            "cmk/gui/test_background_job.py",
            "cmk/gui/watolib/test_automation_background_job.py",
        ],
    ),
    args = [
        "--config-file=$(location @//:pyproject.toml)",
        "--import-mode=importlib",
        "--random-order-bucket=global",
        "--dist=loadfile",
        "--numprocesses=4",
    ],
    data = ["@//:pyproject.toml"] + glob(
        include = [
            # canned data
            "**/_check_form_submit_response",
            "**/test-files/**",
            "**/tree_test_data/**",
            "**/*.json",
            "**/*.jsonl",
            "**/*.log",
            "**/*.yaml",
        ],
        allow_empty = True,
        exclude = ["**/*.py"],
    ) + select({
        "@//:gpl+nonfree_repo": glob(
            [
                "**/*.xml",
                "**/*.pem",
            ],
            allow_empty = True,
        ),
        "@//:gpl_repo": [],
    }),
    main = ":__test__.py",
    visibility = ["//tests:__subpackages__"],
    deps = [
        ":__test__",
        requirement("aiohttp"),
        requirement("apispec-oneofschema"),
        requirement("bcrypt"),
        requirement("beautifulsoup4"),
        requirement("boto3"),
        requirement("botocore"),
        requirement("coverage"),
        requirement("docstring-parser"),
        requirement("exchangelib"),
        requirement("fakeredis"),
        requirement("fastapi"),
        requirement("feedparser"),
        requirement("flask"),
        requirement("google-api-core"),
        requirement("google-api-python-client"),
        requirement("google-auth"),
        requirement("google-cloud-asset"),
        requirement("google-cloud-monitoring"),
        requirement("httpx"),
        requirement("icalendar"),
        requirement("lxml"),
        requirement("marshmallow"),
        requirement("marshmallow-oneofschema"),
        requirement("msal"),
        requirement("mypy-boto3-logs"),
        requirement("numpy"),
        requirement("openapi-spec-validator"),
        requirement("opentelemetry-exporter-otlp"),
        requirement("opentelemetry-instrumentation-fastapi"),
        requirement("opentelemetry-sdk"),
        requirement("pika"),
        requirement("pillow"),
        requirement("polyfactory"),
        requirement("protobuf"),
        requirement("psutil"),
        requirement("pyasn1"),
        requirement("pyghmi"),
        requirement("pyjwt"),
        requirement("pypdf"),
        requirement("pyprof2calltree"),
        requirement("pysaml2"),
        requirement("pysmb"),
        requirement("pytest-asyncio"),
        requirement("pytest-mock"),
        requirement("pytest-random-order"),
        requirement("python-active-directory"),  # missing wheel
        requirement("python-dateutil"),
        requirement("python-ldap"),
        requirement("python-snap7"),
        requirement("pyyaml"),
        requirement("recurring-ical-events"),
        requirement("redis"),
        requirement("requests"),
        requirement("responses"),
        requirement("robotframework"),
        requirement("roman"),
        requirement("setproctitle"),
        requirement("tenacity"),
        requirement("time-machine"),
        requirement("vcrpy"),
        requirement("watchdog"),
        requirement("werkzeug"),
        "//agents/plugins:apache_status",
        "//agents/plugins:mk_jolokia",
        "//agents/plugins:nginx_status",
        "//cmk:cmk_cloud",
        "//cmk:cmk_community",
        "//cmk:cmk_pro",
        "//cmk:cmk_ultimate",
        "//cmk:cmk_ultimatemt",
        "//omd/packages/omd:omdlib",
        "//tests:testlib",
        "//tests/unit:conftest",
    ] + select({
        "@//:gpl+nonfree_repo": [
            requirement("python-multipart"),
            "//non-free/packages/cmc-protocols:py_config_proto",
            "//non-free/packages/cmc-protocols:py_cycletime_proto",
            "//non-free/packages/cmc-protocols:py_state_proto",
            "//non-free/packages/cmk-mknotifyd",
        ],
        "@//:gpl_repo": [],
    }),
)

py_test(
    name = "allow_background_jobs",
    size = "medium",
    srcs = [
        "__test__.py",
        "cmk/gui/common_fixtures.py",
        "cmk/gui/conftest.py",
        "cmk/gui/nonfree/pro/agent_bakery/test_bake_agents.py",
        "cmk/gui/nonfree/pro/agent_bakery/test_misc.py",
        "cmk/gui/test_background_job.py",
        "cmk/gui/users.py",
        "cmk/gui/watolib/test_automation_background_job.py",
        "cmk/web_test_app.py",
    ],
    args = [
        "--config-file=$(location @//:pyproject.toml)",
        "--import-mode=importlib",
        "--random-order-bucket=global",
        "--dist=loadfile",
        "--numprocesses=4",
    ],
    data = ["@//:pyproject.toml"],
    main = ":__test__.py",
    visibility = ["//tests:__subpackages__"],
    deps = [
        ":__test__",
        requirement("pytest-mock"),
        requirement("pytest-random-order"),
        "//cmk:cmk_cloud",
        "//cmk:cmk_community",
        "//cmk:cmk_pro",
        "//cmk:cmk_ultimate",
        "//cmk:cmk_ultimatemt",
        "//tests:testlib",
        "//tests/unit:conftest",
    ],
)
