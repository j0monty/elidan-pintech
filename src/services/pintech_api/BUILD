poetry_requirements(
    name="deps"
)

python_sources(
    name='lib',
    dependencies=[
        # we explicitly depend on the sources in our common module
        "src/common:lib",
        # and also on this own module's deps, specified above
        "src/services/pintech_api:deps",
    ]
)

pex_binary(
    name='pintech_api-server',
    entry_point='main.py',
    dependencies=[
        ':lib',
    ],
    restartable=True
)

pex_binary(
    name='pintech_api-migrate',
    entry_point='migrate.py',
    dependencies=[
        ':lib',
    ],
    restartable=True
)

