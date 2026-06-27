import sys

filepath = 'backend/app/models/alert.py'
with open(filepath, 'r') as f:
    content = f.read()

search_block = """    __table_args__ = (
        Index("ix_alert_status_triggered_at", status, triggered_at.desc()),
        # Partial index for acknowledged_by to avoid indexing NULLs
        Index("ix_alert_acknowledged_by", acknowledged_by, postgres_where=(acknowledged_by != None)),
    )"""

replace_block = """    __table_args__ = (
        Index("ix_alert_status_triggered_at", status, triggered_at.desc()),
        # Partial index for acknowledged_by to avoid indexing NULLs
        Index("ix_alert_acknowledged_by", acknowledged_by, postgresql_where=(acknowledged_by != None)),
    )"""

if search_block in content:
    content = content.replace(search_block, replace_block)
    with open(filepath, 'w') as f:
        f.write(content)
    print("Patched alert.py")
else:
    print("Could not find block in alert.py")
