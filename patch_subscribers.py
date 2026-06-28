import re

with open("backend/app/core/subscribers.py", "r") as f:
    content = f.read()

# Remove the debug logging I added
content = re.sub(r'        # debug\n        all_users = await session\.execute\(select\(User\)\)\n        logger\.info\(f"All Users: \{all_users\.scalars\(\)\.all\(\)\}"\)\n        all_ud = await session\.execute\(select\(user_district_association\)\)\n        logger\.info\(f"All UD: \{all_ud\.all\(\)\}"\)', '', content)
# Restore the query where clause to its proper state (Numeric comparison might just be fine with integer, but let's keep it as risk_score * 100 since User.alert_threshold is Integer)

with open("backend/app/core/subscribers.py", "w") as f:
    f.write(content)
