DATABASE_URL = "postgres://dbtestcase4:dbtestcase4@dbtestcase4:5432/dbtestcase4"

TORTOISE_ORM = {
    "connections": {"default": DATABASE_URL},
    "apps": {
        "models": {
            "models": ["models", "aerich.models"],
            "default_connection": "default",
        },
    },
}
