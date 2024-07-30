python_sources(
    name="lib",
    dependencies=[
        "src/services/pintech_api:pintech_api-server",
    ]
)

pex_binary(
    name="unit_tests",
    entry_point="unit_tests.py",
    dependencies=[
        ":lib"
    ]
)