filegroup(
    name = "srcs",
    srcs = glob(
        ["**"],
        exclude = [
            "BUILD",
            "**/OWNERS",
            "**/.f12",
        ],
    ),
    visibility = ["//visibility:public"],
)

sh_library(
    name = "agents_z_os_sh",
    srcs = [
        "check_mk_agent.wrapper",
    ],
)
