import re

with open('backend/app/core/resilience.py', 'r') as f:
    content = f.read()

# Replace the naive kwargs check with a simpler approach or signature bind.
# Let's just trust the developer's flag and not enforce kwargs.
# If they used with_retry(idempotent_required=False), they are accepting the risk.
# If they used with_retry(idempotent_required=True), we assume the function itself is idempotent or handles it.
# Wait, the review said: "trust the developer's boolean flag entirely".

new_content = re.sub(
    r"if idempotent_required and not kwargs\.get\('idempotency_key'\) and not kwargs\.get\('objectID'\):.*?pass",
    r"",
    content,
    flags=re.DOTALL
)

new_content = re.sub(
    r"if idempotent_required and not kwargs\.get\('idempotency_key'\) and not kwargs\.get\('objectID'\):.*?raise",
    r"",
    new_content,
    flags=re.DOTALL
)

with open('backend/app/core/resilience.py', 'w') as f:
    f.write(new_content)
