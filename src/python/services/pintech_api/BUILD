poetry_requirements(name="deps")

python_sources(
    name="lib",
    dependencies=[
        # we explicitly depend on the sources in our common module
        "src/python/common:lib",
        "src/python/config:lib",
        # and also on this own module"s deps, specified above
        "src/python/services/pintech_api:deps",
    ],
)


resources(
    name="config_files",
    sources=["uvicorn_disable_logging.json"],
)

pex_binary(
    name="pintech_api-server",
    entry_point="main.py",
    dependencies=[
        ":lib",
        ":config_files"
    ],
    restartable=True,
)

pex_binary(
    name="pintech_api-migrate",
    entry_point="migrate.py",
    dependencies=[
        ":lib",
        ":config_files"
    ],
    restartable=True,
)
