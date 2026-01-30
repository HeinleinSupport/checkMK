load("@aspect_rules_py//py:defs.bzl", "py_binary")
load("@cmk_requirements//:requirements.bzl", "requirement")

package(default_visibility = ["//visibility:public"])

py_binary(
    name = "resolve",
    srcs = ["resolve.py"],
)

py_binary(
    name = "register",
    srcs = ["register.py"],
    deps = [
        requirement("docker"),
        requirement("pyyaml"),
    ],
)
