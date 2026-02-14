load("@aspect_rules_py//py:defs.bzl", "py_library")
load("@cmk_requirements//:requirements.bzl", "requirement")

package(default_visibility = ["//cmk:__subpackages__"])

exports_files([
    "nonfree/pro/dcd/.f12",
    "password_store/cli.py",
])

py_library(
    name = "cmk_utils",
    srcs = glob(
        include = ["**/*.py"],
        exclude = [
            "**/community/**",
            "**/nonfree/**",
        ],
    ),
    deps = [
        "//packages/cmk-ccc:config-path",
        "//packages/cmk-ccc:debug",
        "//packages/cmk-ccc:exceptions",
        "//packages/cmk-ccc:hostaddress",
        "//packages/cmk-ccc:i18n",
        "//packages/cmk-ccc:plugin-registry",
        "//packages/cmk-ccc:regex",
        "//packages/cmk-ccc:site",
        "//packages/cmk-ccc:store",
        "//packages/cmk-ccc:tty",
        "//packages/cmk-ccc:user",
        "//packages/cmk-ccc:version",
        "//packages/cmk-crypto",
        "//packages/cmk-events",
        "//packages/cmk-livestatus-client:py_livestatus",
        "//packages/cmk-plugin-apis:agent_based",
        "//packages/cmk-plugin-apis:password_store",
        "//packages/cmk-trace",
        "//packages/cmk-werks",
        requirement("azure-identity"),
        requirement("azure-storage-blob"),
        requirement("boto3"),
        requirement("cryptography"),
        requirement("GitPython"),
        requirement("jinja2"),
        requirement("pillow"),
        requirement("pydantic"),
        requirement("pyopenssl"),
        requirement("python-dateutil"),
        requirement("pyyaml"),
        requirement("redis"),
        requirement("requests"),
        requirement("urllib3"),
    ],
)

py_library(
    name = "cmk_utils_community",
    srcs = glob(
        include = ["**/community/**/*.py"],
        allow_empty = True,
    ),
    imports = ["../.."],
)

py_library(
    name = "cmk_utils_pro",
    srcs = glob(
        include = ["**/nonfree/**/pro/**/*.py"],
        allow_empty = True,
    ),
    imports = ["../.."],
    deps = [
        ":cmk_utils",
        "//packages/cmk-ccc:exceptions",
        "//packages/cmk-ccc:i18n",
        "//packages/cmk-ccc:resulttype",
        "//packages/cmk-ccc:store",
        "//packages/cmk-ccc:version",
        "//packages/cmk-crypto",
        "//packages/cmk-livestatus-client:py_livestatus",
        requirement("pydantic"),
        requirement("python-dateutil"),
    ],
)

py_library(
    name = "cmk_utils_cloud",
    srcs = glob(
        include = ["**/nonfree/**/cloud/**/*.py"],
        allow_empty = True,
    ),
    imports = ["../.."],
    deps = [
        ":cmk_utils",
        "//packages/cmk-ccc:resulttype",
        "//packages/cmk-crypto",
        requirement("python-dateutil"),
        requirement("pydantic"),
    ],
)

py_library(
    name = "cmk_utils_ultimate",
    srcs = glob(
        include = ["**/nonfree/**/ultimate/**/*.py"],
        allow_empty = True,
    ),
    imports = ["../.."],
    deps = [
        ":cmk_utils",
        "//packages/cmk-ccc:resulttype",
        requirement("python-dateutil"),
    ],
)

py_library(
    name = "cmk_utils_ultimatemt",
    srcs = glob(
        include = ["**/nonfree/**/ultimatemt/**/*.py"],
        allow_empty = True,
    ),
    imports = ["../.."],
    deps = [
        ":cmk_utils",
        "//packages/cmk-ccc:resulttype",
        requirement("python-dateutil"),
    ],
)
