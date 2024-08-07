run_shell_command(
    name="run_api_with_db",
    command=". src/docker/mongo/start_mongodb.sh && pants run src/python/services/pintech_api:pintech_api-server",
)

run_shell_command(
    name="run_api_with_db_debug",
    command=". src/docker/mongo/start_mongodb.sh && watchmedo auto-restart -d ./src/python -R -p '*.py' -- pants run --debug-adapter src/python/services/pintech_api/main.py",
)

shell_sources(
    name="root",
)
