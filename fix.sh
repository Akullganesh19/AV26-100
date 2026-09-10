cat << 'PATCH' > diff.txt
<<<<<<< SEARCH
# Use the dedicated test database created in the previous step
TEST_DATABASE_URL = str(settings.DATABASE_URL) + "_test"
=======
# Use the dedicated test database created in the previous step
db_url_str = str(settings.DATABASE_URL)
TEST_DATABASE_URL = db_url_str if db_url_str.endswith("_test") else f"{db_url_str}_test"
>>>>>>> REPLACE
PATCH
