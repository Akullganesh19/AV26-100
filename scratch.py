db_url = "postgresql+asyncpg://postgres:postgres@localhost/episense_test"
if not db_url.endswith("_test"):
    db_url += "_test"
print(db_url)
