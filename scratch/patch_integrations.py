import re

with open("backend/app/api/integrations.py", "r") as f:
    content = f.read()

# Make sure utils is imported
if "from app.core.utils import with_retry" not in content:
    content = "from app.core.utils import with_retry\n" + content

# Replace await asyncio.to_thread with await with_retry(asyncio.to_thread, ...
content = re.sub(r'await asyncio\.to_thread\(self\.index\.save_object, district_data\)', r'await with_retry(asyncio.to_thread, self.index.save_object, district_data, max_attempts=3)', content)
content = re.sub(r'await asyncio\.to_thread\(self\.sg\.send, message\)', r'await with_retry(asyncio.to_thread, self.sg.send, message, max_attempts=3)', content)
content = re.sub(r'upload_result = cloudinary\.uploader\.upload\(\n\s+file_bytes,\n\s+resource_type="raw",\n\s+public_id=f"reports/district_\{district_id\}",\n\s+format="pdf"\n\s+\)', r'upload_result = await with_retry(asyncio.to_thread, cloudinary.uploader.upload, file_bytes, resource_type="raw", public_id=f"reports/district_{district_id}", format="pdf", max_attempts=3)', content)

# But we need graceful degradation to prevent cascading failures.
# Let's write the updated file directly.
