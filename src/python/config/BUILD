poetry_requirements(name="deps")

python_sources(
    name="common",
    dependencies=[
        # we explicitly depend on the sources in our common module
        "src/python/common:lib",
    ],
)


resources(
    name="config_files",
    sources=["settings.toml", ".secrets.toml"],
)

python_sources(
    name="lib",
    dependencies=[
        "src/python/config:deps",
         ":config_files",
    ],
)
