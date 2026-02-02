load("@aspect_rules_js//js:defs.bzl", "js_library")
load("@bazel_env.bzl", "bazel_env")
load("@bazel_skylib//rules:native_binary.bzl", "native_binary")
load("@cmk_requirements//:requirements.bzl", "requirement")
load("@npm//:defs.bzl", "npm_link_all_packages")
load("@npm//bazel/tools:npm-groovy-lint/package_json.bzl", groovy_bin = "bin")
load("@rules_mypy//mypy:mypy.bzl", "mypy_cli")
load("@rules_python//python:defs.bzl", "py_binary")
load("@rules_python//python/entry_points:py_console_script_binary.bzl", "py_console_script_binary")
load("@rules_uv//uv:pip.bzl", "pip_compile")
load("@tools_requirements//:requirements.bzl", tooling_pip = "requirement")
load("//bazel/rules:sh_expand_template.bzl", "sh_expand_template")

pip_compile(
    name = "requirements",
    requirements_in = "requirements.in",
    requirements_txt = "requirements.txt",
    tags = ["manual"],
)

npm_link_all_packages(name = "node_modules")

js_library(
    name = "prettierrc",
    srcs = ["prettier.config.cjs"],
    visibility = ["//:__subpackages__"],
    deps = [
        ":node_modules/@trivago/prettier-plugin-sort-imports",
    ],
)

groovy_bin.npm_groovy_lint_binary(
    name = "groovy-lint",
    data = ["//bazel/tools:.groovylintrc.json"],
    env = {"BAZEL_BINDIR": "."},
    fixed_args = [
        "--config=\"$$JS_BINARY__RUNFILES\"/$(rlocationpath //bazel/tools:.groovylintrc.json)",
    ],
)

mypy_cli(
    name = "mypy_cli_original",
    mypy_requirement = requirement("mypy"),
    python_version = "3.13",
    deps = [
        # for `plugins = ["pydantic.mypy"]`
        requirement("pydantic"),
    ],
)

py_console_script_binary(
    name = "bandit",
    pkg = requirement("bandit"),
    tags = [
        "manual",
        "no-mypy",
    ],
)

py_console_script_binary(
    name = "semgrep",
    pkg = tooling_pip("semgrep"),
    script = "pysemgrep",
    tags = [
        "manual",
        "no-mypy",
    ],
)

# Custom mypy wrapper that filters problematic MYPYPATH entries
py_binary(
    name = "mypy_cli",
    srcs = ["mypy_wrapper.py"],
    data = [":mypy_cli_original"],
    main = "mypy_wrapper.py",
    deps = [
        requirement("mypy"),
        requirement("pydantic"),
    ],
)

native_binary(
    name = "clang_tidy",
    src = "@clang-linux-x86_64//:bin/clang-tidy",
)

filegroup(
    name = "clang_tidy_config",
    srcs = ["//:.clang-tidy"],
    visibility = ["//visibility:public"],
)

alias(
    name = "uv",
    actual = "@multitool//tools/uv",
)

bazel_env(
    name = "bazel_env",
    toolchains = {},
    tools = {
        "bandit": ":bandit",
        "genhtml": "@lcov//:genhtml",
        "mypy": ":mypy_cli_original",
        "osslsigncode": "@osslsigncode",
        "pnpm": "@pnpm",
        "semgrep": ":semgrep",
        "uv": "@multitool//tools/uv",
    },
)

py_binary(
    name = "extract_os_packages",
    srcs = ["extract_os_packages.py"],
    main = "extract_os_packages.py",
    visibility = ["//visibility:public"],
)

[
    sh_expand_template(
        name = name,
        src = "@buildifier_prebuilt//:buildifier",
        data = ["//:buildifier_config"],
        substitutions = {
            "{buildifier_args}": args,
            "{buildifier_bin}": "$(execpath @buildifier_prebuilt//:buildifier)",
            "{config}": "$(execpath //:buildifier_config)",
        },
        template = [
            "#!/bin/bash",
            "set -e",
            'REPO_PATH="${BUILD_WORKSPACE_DIRECTORY:-.}"',
            'find "$REPO_PATH" -type f \\',
            '    \\! -path "${REPO_PATH}/*/build/*" \\',
            '    \\! -path "${REPO_PATH}/container_shadow_workspace_local/*" \\',
            '    \\! -path "${REPO_PATH}/.docker_workspace/*" \\',
            '    \\! -path "${REPO_PATH}/tests/qa-test-data/*" \\',
            '    \\! -path "${REPO_PATH}/.cache/*" \\',
            '    \\! -path "${REPO_PATH}/bazel/registry/*" \\',
            '    \\! -path "${REPO_PATH}/bazel/thirdparty/*" \\',
            '    \\( -name "*.bzl" -o -name "*.sky" -o -name BUILD.bazel -o -name BUILD \\',
            '    -o -name "*.BUILD" -o -name "BUILD.*.bazel" -o -name "BUILD.*.oss" \\',
            '    -o -name "MODULE.bazel" -o -name WORKSPACE -o -name WORKSPACE.bazel \\',
            '    -o -name WORKSPACE.oss -o -name "WORKSPACE.*.bazel" -o -name "WORKSPACE.*.oss" \\) \\',
            '    -print | xargs "$BUILD_WORKSPACE_DIRECTORY/{buildifier_bin}" {buildifier_args} \\',
            '    -config="$BUILD_WORKSPACE_DIRECTORY/{config}" "$@"',
            "",
        ],
        visibility = ["//visibility:public"],
    )
    for name, args in [
        ("buildifier", "--lint=fix"),
        ("buildifier.check", "--lint=warn"),
    ]
]
