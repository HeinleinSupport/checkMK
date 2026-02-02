filegroup(
    name = "srcs",
    srcs = glob(
        include = ["**"],
        exclude = [
            "_*/**",
            ".*",
            "OWNERS",
            "BUILD",
        ],
    ),
    visibility = ["//:__subpackages__"],
)

sh_library(
    name = "doc_documentation_sh",
    srcs = [
        ".f12",
    ],
)
