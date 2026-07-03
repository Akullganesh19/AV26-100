with open("backend/app/models/alert.py", "r") as f:
    content = f.read()

# Fix the warning mentioned in the error logs
content = content.replace("postgres_where", "postgresql_where")

with open("backend/app/models/alert.py", "w") as f:
    f.write(content)
