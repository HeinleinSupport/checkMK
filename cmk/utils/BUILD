load("@aspect_rules_py//py:defs.bzl", "py_library")
load("@cmk_requirements//:requirements.bzl", "requirement")

exports_files([
    "nonfree/pro/dcd/.f12",
    "password_store/cli.py",
    "werks/announce/templates/announce.md.jinja2",
    "werks/announce/templates/announce.txt.jinja2",
])

py_library(
    name = "paths",
    srcs = ["paths.py"],
    imports = ["../.."],
    visibility = ["//visibility:public"],
)

py_library(
    name = "servicename",
    srcs = ["servicename.py"],
    imports = ["../.."],
    visibility = ["//visibility:public"],
)

py_library(
    name = "sectionname",
    srcs = ["sectionname.py"],
    imports = ["../.."],
    visibility = ["//visibility:public"],
)

py_library(
    name = "everythingtype",
    srcs = ["everythingtype.py"],
    imports = ["../.."],
    visibility = ["//visibility:public"],
)

py_library(
    name = "global_ident_type",
    srcs = ["global_ident_type.py"],
    imports = ["../.."],
    visibility = ["//visibility:public"],
)

py_library(
    name = "jsontype",
    srcs = ["jsontype.py"],
    imports = ["../.."],
    visibility = ["//visibility:public"],
)

py_library(
    name = "typing_helpers",
    srcs = ["typing_helpers.py"],
    imports = ["../.."],
    visibility = ["//visibility:public"],
)

py_library(
    name = "metrics",
    srcs = ["metrics.py"],
    imports = ["../.."],
    visibility = ["//visibility:public"],
)

py_library(
    name = "html",
    srcs = ["html.py"],
    imports = ["../.."],
    visibility = ["//visibility:public"],
)

py_library(
    name = "datastructures",
    srcs = ["datastructures.py"],
    imports = ["../.."],
    visibility = ["//visibility:public"],
)

py_library(
    name = "check_utils",
    srcs = ["check_utils.py"],
    imports = ["../.."],
    visibility = ["//visibility:public"],
)

py_library(
    name = "encoding",
    srcs = ["encoding.py"],
    imports = ["../.."],
    visibility = ["//visibility:public"],
)

py_library(
    name = "deprecation_warnings",
    srcs = ["deprecation_warnings.py"],
    imports = ["../.."],
    visibility = ["//visibility:public"],
)

py_library(
    name = "plugin_loader",
    srcs = ["plugin_loader.py"],
    imports = ["../.."],
    visibility = ["//visibility:public"],
)

py_library(
    name = "misc",
    srcs = ["misc.py"],
    imports = ["../.."],
    visibility = ["//visibility:public"],
)

py_library(
    name = "caching",
    srcs = ["caching.py"],
    imports = ["../.."],
    visibility = ["//visibility:public"],
)

py_library(
    name = "parameters",
    srcs = ["parameters.py"],
    imports = ["../.."],
    visibility = ["//visibility:public"],
)

py_library(
    name = "macros",
    srcs = ["macros.py"],
    imports = ["../.."],
    visibility = ["//visibility:public"],
)

py_library(
    name = "experimental_config",
    srcs = ["experimental_config.py"],
    imports = ["../.."],
    visibility = ["//visibility:public"],
)

py_library(
    name = "oauth2_connection",
    srcs = ["oauth2_connection.py"],
    imports = ["../.."],
    visibility = ["//visibility:public"],
)

py_library(
    name = "mrpe_config",
    srcs = ["mrpe_config.py"],
    imports = ["../.."],
    visibility = ["//visibility:public"],
)

py_library(
    name = "ms_teams_constants",
    srcs = ["ms_teams_constants.py"],
    imports = ["../.."],
    visibility = ["//visibility:public"],
)

py_library(
    name = "schedule",
    srcs = ["schedule.py"],
    imports = ["../.."],
    visibility = ["//visibility:public"],
    deps = [
        requirement("python-dateutil"),
    ],
)

py_library(
    name = "msi_patch",
    srcs = ["msi_patch.py"],
    imports = ["../.."],
    visibility = ["//visibility:public"],
    deps = [
        requirement("pyyaml"),
    ],
)

py_library(
    name = "unixsocket_http",
    srcs = ["unixsocket_http.py"],
    imports = ["../.."],
    visibility = ["//visibility:public"],
    deps = [
        requirement("requests"),
        requirement("urllib3"),
    ],
)

py_library(
    name = "statename",
    srcs = ["statename.py"],
    imports = ["../.."],
    visibility = ["//visibility:public"],
    deps = [
        "//packages/cmk-ccc:i18n",
    ],
)

py_library(
    name = "render",
    srcs = ["render.py"],
    imports = ["../.."],
    visibility = ["//visibility:public"],
    deps = [
        "//packages/cmk-ccc:i18n",
    ],
)

py_library(
    name = "dateutils",
    srcs = ["dateutils.py"],
    imports = ["../.."],
    visibility = ["//visibility:public"],
    deps = [
        "//packages/cmk-ccc:i18n",
        requirement("python-dateutil"),
    ],
)

py_library(
    name = "urls",
    srcs = ["urls.py"],
    imports = ["../.."],
    visibility = ["//visibility:public"],
    deps = [
        "//packages/cmk-ccc:regex",
    ],
)

py_library(
    name = "tags",
    srcs = ["tags.py"],
    imports = ["../.."],
    visibility = ["//visibility:public"],
    deps = [
        "//packages/cmk-ccc:exceptions",
        "//packages/cmk-ccc:hostaddress",
        "//packages/cmk-ccc:i18n",
        "//packages/cmk-ccc:site",
    ],
)

py_library(
    name = "agent_registration",
    srcs = ["agent_registration.py"],
    imports = ["../.."],
    visibility = ["//visibility:public"],
    deps = [
        "//packages/cmk-ccc:hostaddress",
    ],
)

py_library(
    name = "automation_config",
    srcs = ["automation_config.py"],
    imports = ["../.."],
    visibility = ["//visibility:public"],
    deps = [
        "//packages/cmk-ccc:site",
    ],
)

py_library(
    name = "object_diff",
    srcs = ["object_diff.py"],
    imports = ["../.."],
    visibility = ["//visibility:public"],
    deps = [
        "//packages/cmk-ccc:i18n",
    ],
)

py_library(
    name = "auto_queue",
    srcs = ["auto_queue.py"],
    imports = ["../.."],
    visibility = ["//visibility:public"],
    deps = [
        "//packages/cmk-ccc:hostaddress",
    ],
)

py_library(
    name = "man_pages",
    srcs = ["man_pages.py"],
    imports = ["../.."],
    visibility = ["//visibility:public"],
    deps = [
        "//packages/cmk-ccc:debug",
        "//packages/cmk-ccc:exceptions",
        "//packages/cmk-ccc:i18n",
        "//packages/cmk-ccc:tty",
    ],
)

py_library(
    name = "escaping",
    srcs = ["escaping.py"],
    imports = ["../.."],
    visibility = ["//visibility:public"],
    deps = [
        ":urls",
    ],
)

py_library(
    name = "timeperiod",
    srcs = ["timeperiod.py"],
    imports = ["../.."],
    visibility = ["//visibility:public"],
    deps = [
        ":dateutils",
        "//packages/cmk-ccc:i18n",
        requirement("python-dateutil"),
    ],
)

py_library(
    name = "labels",
    srcs = ["labels.py"],
    imports = ["../.."],
    visibility = ["//visibility:public"],
    deps = [
        ":paths",
        ":servicename",
        "//packages/cmk-ccc:exceptions",
        "//packages/cmk-ccc:hostaddress",
        "//packages/cmk-ccc:site",
        "//packages/cmk-ccc:store",
    ],
)

py_library(
    name = "redis",
    srcs = ["redis.py"],
    imports = ["../.."],
    visibility = ["//visibility:public"],
    deps = [
        ":paths",
        "//packages/cmk-ccc:exceptions",
        requirement("redis"),
    ],
)

py_library(
    name = "caching_redis",
    srcs = ["caching_redis.py"],
    imports = ["../.."],
    visibility = ["//visibility:public"],
    deps = [
        ":caching",
        ":redis",
        requirement("redis"),
    ],
)

py_library(
    name = "local_secrets",
    srcs = ["local_secrets.py"],
    imports = ["../.."],
    visibility = ["//visibility:public"],
    deps = [
        ":paths",
        "//packages/cmk-ccc:store",
        "//packages/cmk-ccc:user",
        "//packages/cmk-crypto",
    ],
)

py_library(
    name = "images",
    srcs = ["images.py"],
    imports = ["../.."],
    visibility = ["//visibility:public"],
    deps = [
        requirement("pillow"),
    ],
)

py_library(
    name = "mail",
    srcs = ["mail.py"],
    imports = ["../.."],
    visibility = ["//visibility:public"],
    deps = [
        ":paths",
        "//packages/cmk-ccc:store",
        "//packages/cmk-ccc:version",
    ],
)

py_library(
    name = "setup_search_index",
    srcs = ["setup_search_index.py"],
    imports = ["../.."],
    visibility = ["//visibility:public"],
    deps = [
        ":paths",
        "//packages/cmk-ccc:store",
    ],
)

py_library(
    name = "msi_engine",
    srcs = ["msi_engine.py"],
    imports = ["../.."],
    visibility = ["//visibility:public"],
    deps = [
        ":msi_patch",
        "//packages/cmk-ccc:version",
    ],
)

py_library(
    name = "visuals",
    srcs = ["visuals.py"],
    imports = ["../.."],
    visibility = ["//visibility:public"],
    deps = [
        ":paths",
    ],
)

py_library(
    name = "encryption",
    srcs = ["encryption.py"],
    imports = ["../.."],
    visibility = ["//visibility:public"],
    deps = [
        "//packages/cmk-ccc:exceptions",
        "//packages/cmk-crypto",
        requirement("pyopenssl"),
    ],
)

py_library(
    name = "log",
    srcs = glob(["log/**/*.py"]),
    imports = ["../.."],
    visibility = ["//visibility:public"],
    deps = [
        ":jsontype",
        ":paths",
        "//packages/cmk-ccc:tty",
    ],
)

py_library(
    name = "config_warnings",
    srcs = ["config_warnings.py"],
    imports = ["../.."],
    visibility = ["//visibility:public"],
    deps = [
        ":log",
        "//packages/cmk-ccc:tty",
    ],
)

py_library(
    name = "ip_lookup",
    srcs = ["ip_lookup.py"],
    imports = ["../.."],
    visibility = ["//visibility:public"],
    deps = [
        ":caching",
        ":log",
        ":paths",
        "//packages/cmk-ccc:debug",
        "//packages/cmk-ccc:exceptions",
        "//packages/cmk-ccc:hostaddress",
        "//packages/cmk-ccc:store",
    ],
)

py_library(
    name = "certs",
    srcs = ["certs.py"],
    imports = ["../.."],
    visibility = ["//visibility:public"],
    deps = [
        ":log",
        "//packages/cmk-ccc:site",
        "//packages/cmk-ccc:user",
        "//packages/cmk-crypto",
        requirement("cryptography"),
        requirement("python-dateutil"),
    ],
)

py_library(
    name = "crypto",
    srcs = ["crypto/__init__.py"],
    imports = ["../.."],
    visibility = ["//visibility:public"],
)

py_library(
    name = "rulesets",
    srcs = glob(["rulesets/**/*.py"]),
    imports = ["../.."],
    visibility = ["//visibility:public"],
    deps = [
        ":global_ident_type",
        ":labels",
        ":parameters",
        ":paths",
        ":servicename",
        ":tags",
        "//packages/cmk-ccc:debug",
        "//packages/cmk-ccc:exceptions",
        "//packages/cmk-ccc:hostaddress",
        "//packages/cmk-ccc:regex",
        "//packages/cmk-trace",
    ],
)

py_library(
    name = "password_store",
    srcs = glob(["password_store/**/*.py"]),
    imports = ["../.."],
    visibility = ["//visibility:public"],
    deps = [
        ":global_ident_type",
        ":paths",
        "//packages/cmk-ccc:config-path",
        "//packages/cmk-ccc:exceptions",
        "//packages/cmk-ccc:store",
        "//packages/cmk-plugin-apis:password_store",
    ],
)

py_library(
    name = "http_proxy_config",
    srcs = ["http_proxy_config.py"],
    imports = ["../.."],
    visibility = ["//visibility:public"],
    deps = [
        ":password_store",
    ],
)

py_library(
    name = "licensing",
    srcs = glob(["licensing/**/*.py"]),
    imports = ["../.."],
    visibility = ["//visibility:public"],
    deps = [
        ":automation_config",
        ":paths",
        "//packages/cmk-ccc:plugin-registry",
        "//packages/cmk-ccc:site",
        "//packages/cmk-ccc:store",
        "//packages/cmk-ccc:version",
        "//packages/cmk-livestatus-client:py_livestatus",
        requirement("python-dateutil"),
    ],
)

py_library(
    name = "backup",
    srcs = glob(["backup/**/*.py"]),
    imports = ["../.."],
    visibility = ["//visibility:public"],
    deps = [
        ":password_store",
        ":paths",
        "//packages/cmk-ccc:exceptions",
        "//packages/cmk-ccc:i18n",
        "//packages/cmk-ccc:store",
        "//packages/cmk-ccc:version",
        "//packages/cmk-crypto",
        requirement("azure-identity"),
        requirement("azure-storage-blob"),
        requirement("boto3"),
        requirement("pydantic"),
    ],
)

py_library(
    name = "prediction",
    srcs = glob(["prediction/**/*.py"]),
    imports = ["../.."],
    visibility = ["//visibility:public"],
    deps = [
        ":log",
        ":misc",
        ":paths",
        ":servicename",
        "//packages/cmk-ccc:hostaddress",
        "//packages/cmk-livestatus-client:py_livestatus",
        "//packages/cmk-plugin-apis:agent_based",
        requirement("pydantic"),
    ],
)

py_library(
    name = "werks",
    srcs = glob(["werks/**/*.py"]),
    data = glob(["werks/**/templates/**"]),
    imports = ["../.."],
    visibility = ["//visibility:public"],
    deps = [
        ":mail",
        ":paths",
        "//packages/cmk-ccc:store",
        "//packages/cmk-ccc:version",
        "//packages/cmk-werks",
        requirement("GitPython"),
        requirement("jinja2"),
    ],
)

py_library(
    name = "notify_types",
    srcs = ["notify_types.py"],
    imports = ["../.."],
    visibility = ["//visibility:public"],
    deps = [
        ":rulesets",
        ":tags",
        ":timeperiod",
        "//packages/cmk-events",
        requirement("pydantic"),
    ],
)

py_library(
    name = "notify",
    srcs = ["notify.py"],
    imports = ["../.."],
    visibility = ["//visibility:public"],
    deps = [
        ":labels",
        ":notify_types",
        ":paths",
        ":servicename",
        ":tags",
        "//packages/cmk-ccc:config-path",
        "//packages/cmk-ccc:exceptions",
        "//packages/cmk-ccc:hostaddress",
        "//packages/cmk-ccc:i18n",
        "//packages/cmk-ccc:store",
    ],
)

py_library(
    name = "host_storage",
    srcs = ["host_storage.py"],
    imports = ["../.."],
    visibility = ["//visibility:public"],
    deps = [
        ":labels",
        ":rulesets",
        ":tags",
        "//packages/cmk-ccc:hostaddress",
        "//packages/cmk-ccc:store",
    ],
)

py_library(
    name = "cmk_utils",
    visibility = ["//:__subpackages__"],
    deps = [
        "agent_registration",
        "auto_queue",
        "automation_config",
        "backup",
        "caching",
        "caching_redis",
        "certs",
        "check_utils",
        "config_warnings",
        "crypto",
        "datastructures",
        "dateutils",
        "deprecation_warnings",
        "encoding",
        "encryption",
        "escaping",
        "everythingtype",
        "experimental_config",
        "global_ident_type",
        "host_storage",
        "html",
        "http_proxy_config",
        "images",
        "ip_lookup",
        "jsontype",
        "labels",
        "licensing",
        "local_secrets",
        "log",
        "macros",
        "mail",
        "man_pages",
        "metrics",
        "misc",
        "mrpe_config",
        "ms_teams_constants",
        "msi_engine",
        "msi_patch",
        "notify",
        "notify_types",
        "oauth2_connection",
        "object_diff",
        "parameters",
        "password_store",
        "paths",
        "plugin_loader",
        "prediction",
        "redis",
        "render",
        "rulesets",
        "schedule",
        "sectionname",
        "servicename",
        "setup_search_index",
        "statename",
        "tags",
        "timeperiod",
        "typing_helpers",
        "unixsocket_http",
        "urls",
        "visuals",
        "werks",
    ],
)

py_library(
    name = "cmk_utils_pro",
    srcs = glob(
        include = [
            "nonfree/**/pro/**/*.py",
            "nonfree/**/*.py",
        ],
        allow_empty = True,
        exclude = [
            "nonfree/**/cloud/**",
            "nonfree/**/ultimate/**",
            "nonfree/**/ultimatemt/**",
        ],
    ),
    imports = ["../.."],
    visibility = ["//:__subpackages__"],
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
    name = "cmk_utils_ultimate",
    srcs = glob(
        include = ["nonfree/**/ultimate/**/*.py"],
        allow_empty = True,
    ),
    imports = ["../.."],
    visibility = ["//:__subpackages__"],
    deps = [
        ":cmk_utils",
    ],
)

py_library(
    name = "cmk_utils_cloud",
    srcs = glob(
        include = ["nonfree/**/cloud/**/*.py"],
        allow_empty = True,
    ),
    imports = ["../.."],
    visibility = ["//:__subpackages__"],
    deps = [
        ":cmk_utils",
        "//packages/cmk-crypto",
        requirement("pydantic"),
    ],
)

py_library(
    name = "cmk_utils_ultimatemt",
    srcs = glob(
        include = ["nonfree/**/ultimatemt/**/*.py"],
        allow_empty = True,
    ),
    imports = ["../.."],
    visibility = ["//:__subpackages__"],
    deps = [
        ":cmk_utils",
    ],
)
