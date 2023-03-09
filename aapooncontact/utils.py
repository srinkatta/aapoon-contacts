def get_env_database(env: str) -> str:
    if env == "dev":
        return "dev.sqlite3"
    elif env == "staging":
        return "staging.sqlite3"
    elif env == "prod":
        return "prod.sqlite3"
    else:
        return "local.sqlite3"
