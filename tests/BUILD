load("@aspect_rules_py//py:defs.bzl", "py_library")
load("@cmk_requirements//:requirements.bzl", "requirement")

package(default_visibility = [":__subpackages__"])

exports_files(["dev-requirements.in"])

py_library(
    name = "testlib",
    testonly = True,
    srcs = ["__init__.py"] + glob(
        include = ["testlib/**/*.py"],
    ),
    data = glob(
        include = ["testlib/**"],
        allow_empty = True,
        exclude = ["testlib/**/*.py"],
    ),
    imports = [".."],
    deps = [
        "//cmk:cmk_cmk",
        requirement("beautifulsoup4"),
        requirement("clickhouse-connect"),
        requirement("cryptography"),
        requirement("docker"),
        requirement("dockerpty"),
        requirement("fastapi"),
        requirement("pexpect"),
        requirement("playwright"),
        requirement("psutil"),
        requirement("pyjwt"),
        requirement("pyyaml"),
        requirement("pytest"),
        requirement("pytest-check"),
        requirement("requests"),
    ] + select({
        "//:gpl+nonfree_repo": ["//cmk:cmk_cloud"],
        "//:gpl_repo": [],
    }),
)

py_library(
    name = "conftest",
    testonly = True,
    srcs = ["conftest.py"],
    deps = [
        ":testlib",
        requirement("playwright"),
        requirement("pytest"),
        requirement("pytest-check"),
        requirement("pytest-metadata"),
    ],
)

py_library(
    name = "testlib_system_level",
    testonly = True,
    srcs = ["__init__.py"] + glob(
        include = ["testlib/**/*.py"],
        exclude = ["testlib/unit/**"],
    ),
    data = glob(
        include = ["testlib/**"],
        allow_empty = True,
        exclude = ["testlib/**/*.py"],
    ),
    imports = [".."],
    deps = [
        "//cmk:cmk_cmk",
        requirement("beautifulsoup4"),
        requirement("clickhouse-connect"),
        requirement("cryptography"),
        requirement("docker"),
        requirement("dockerpty"),
        requirement("fastapi"),
        requirement("pexpect"),
        requirement("playwright"),
        requirement("psutil"),
        requirement("pyjwt"),
        requirement("pytest"),
        requirement("pytest-check"),
        requirement("pyyaml"),
        requirement("requests"),
    ] + select({
        "//:gpl+nonfree_repo": ["//cmk:cmk_cloud"],
        "//:gpl_repo": [],
    }),
)

py_library(
    name = "testlib_unit",
    testonly = True,
    srcs = ["__init__.py"] + glob(
        include = [
            "testlib/unit/**/*.py",
            "testlib/common/**/*.py",
        ],
    ),
    data = glob(
        include = [
            "testlib/unit/**",
            "testlib/common/**",
        ],
        allow_empty = True,
        exclude = [
            "testlib/unit/**/*.py",
            "testlib/common/**/*.py",
        ],
    ),
    imports = [".."],
    deps = [
        ":testlib",
        "//cmk:cmk_cmk",
        requirement("pexpect"),
        requirement("pytest"),
        requirement("pyyaml"),
    ] + select({
        "//:gpl+nonfree_repo": ["//cmk:cmk_pro"],
        "//:gpl_repo": [],
    }),
)

sh_library(
    name = "tests_sh",
    srcs = [
        "performance/database/mk_client_cert.sh",
        "performance/database/mk_server_cert.sh",
        "performance/perftest.sh",
        "scripts/find_modified_lock_files",
        "scripts/run_code_coverage.sh",
        "scripts/setup_openldap.sh",
        "scripts/setup_postfix.sh",
        "scripts/teardown_openldap.sh",
        "scripts/teardown_postfix.sh",
        "scripts/verify_test_python_files.sh",
        "unit-shell/agents/plugins/test_common_inventory_parts.sh",
        "unit-shell/agents/plugins/test_common_plugin_parts.sh",
        "unit-shell/agents/plugins/test_ibm_mq.sh",
        "unit-shell/agents/plugins/test_kaspersky_av.sh",
        "unit-shell/agents/plugins/test_mk_inventory.sh",
        "unit-shell/agents/plugins/test_mk_oracle.sh",
        "unit-shell/agents/plugins/test_mk_redis.sh",
        "unit-shell/agents/plugins/test_mk_sap_hana.sh",
        "unit-shell/agents/plugins/test_mk_tsm.sh",
        #        "unit-shell/agents/plugins/test_netstat.linux.sh",
        "unit-shell/agents/plugins/test_symantec_av.sh",
        "unit-shell/agents/scripts/super-server/0_systemd/test_setup.sh",
        "unit-shell/agents/scripts/super-server/test_setup.sh",
        "unit-shell/agents/test_bourne_again_shell.sh",
        "unit-shell/agents/test_bourne_shell.sh",
        "unit-shell/agents/test_common_agent_parts.sh",
        "unit-shell/agents/test_common_mk-job_parts.sh",
        "unit-shell/agents/test_current_shell.sh",
        "unit-shell/agents/test_encryption_linux.sh",
        "unit-shell/agents/test_encryption_solaris.sh",
        "unit-shell/agents/test_get_epoch.sh",
        "unit-shell/agents/test_korn_shell.sh",
        "unit-shell/agents/test_korn_shell_93.sh",
        "unit-shell/agents/test_log_section_time.sh",
        "unit-shell/agents/test_mk-job.sh",
        "unit-shell/agents/test_mrpe.sh",
        "unit-shell/agents/test_plugin_execution.sh",
        "unit-shell/agents/test_run_cached.sh",
        "unit-shell/agents/test_section_checkmk_linux.sh",
        "unit-shell/agents/test_section_local_linux.sh",
        "unit-shell/agents/test_section_nfs_mounts.sh",
        "unit-shell/agents/test_section_uptime_aix.sh",
        "unit-shell/agents/test_set_up_path.sh",
        "unit-shell/agents/test_z_shell.sh",
        "unit-shell/relay/mocks.sh",
        "unit-shell/relay/test_args.sh",
        "unit-shell/relay/test_call_order.sh",
        "unit-shell/relay/test_podman.sh",
        "unit-shell/relay/test_prereqs.sh",
        "unit-shell/relay/test_registration.sh",
        "unit-shell/relay/test_systemctl_failure.sh",
        "unit-shell/relay/test_systemd_files.sh",
        "unit-shell/relay/test_update_manager.sh",
        "unit-shell/relay/test_user_linger.sh",
        "unit-shell/runner.sh",
        "//agents/plugins:agents_plugins_sh",
        "//agents:agents_sh",
        "//omd/non-free/relay:omd_non-free_relay_sh",
    ],
)
