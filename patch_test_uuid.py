with open("backend/tests/test_synapse.py", "r") as f:
    content = f.read()

# user.email is unique. if tests run twice or something it can conflict, but this test passes locally on isolation, wait, no it fails.
# "No users matching alert threshold".
# The district_id is passed as a string. But it's UUID in the database. `user_district_association.c.district_id == district_id` where `district_id` is a string `alert_id: str, district_id: str`. In asyncpg, string against UUID might fail to match. We should cast it or pass the UUID.
