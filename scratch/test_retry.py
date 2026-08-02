import asyncio

async def with_retry(func, *args, max_attempts=3, base_delay=0.1, **kwargs):
    attempt = 1
    while True:
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if attempt >= max_attempts:
                print(f"Failed after {max_attempts} attempts: {e}")
                raise
            delay = base_delay * (2 ** (attempt - 1))
            print(f"Transient failure (attempt {attempt}/{max_attempts}): {e}. Retrying in {delay}s...")
            await asyncio.sleep(delay)
            attempt += 1

def my_sync_upload(data, resource_type="default"):
    print(f"Uploading {data} as {resource_type}")
    raise ValueError("Network error!")

async def main():
    try:
        await with_retry(
            asyncio.to_thread,
            my_sync_upload,
            "test_data",
            resource_type="raw",
            max_attempts=3
        )
    except Exception as e:
        print("Caught ultimate failure!")

asyncio.run(main())
