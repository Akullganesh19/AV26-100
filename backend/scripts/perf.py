import asyncio
import time
import uuid

# Mock classes to measure performance without a real DB
class MockQuery:
    def scalars(self):
        return self
    def first(self):
        return None

class MockSession:
    def __init__(self):
        self.adds = 0
    async def execute(self, q):
        # Simulate small network/DB latency
        await asyncio.sleep(0.005)
        return MockQuery()
    def add(self, obj):
        self.adds += 1
    async def commit(self): pass
    async def flush(self): pass
    async def refresh(self, obj): pass

DISTRICTS = [{"id": str(i), "name": f"D{i}", "state": "S", "state_code": "S", "lat": 0, "lng": 0, "pop": 0, "area": 0} for i in range(100)]

async def run_original():
    session = MockSession()

    start_time = time.time()
    district_instances = []
    for d in DISTRICTS:
        # N+1 approach
        q = await session.execute("select...")
        existing = q.scalars().first()
        if not existing:
            session.add(d)
            district_instances.append(d)
        else:
            district_instances.append(existing)

    print(f"Original logic time: {time.time() - start_time:.4f}s")

async def run_optimized():
    session = MockSession()

    start_time = time.time()
    district_instances = []

    # 1 query
    q = await session.execute("select IN ...")
    existing_districts = {("D", "S"): d for d in []}

    for d in DISTRICTS:
        existing = existing_districts.get((d["name"], d["state"]))
        if not existing:
            session.add(d)
            district_instances.append(d)
        else:
            district_instances.append(existing)

    print(f"Optimized logic time: {time.time() - start_time:.4f}s")


if __name__ == "__main__":
    asyncio.run(run_original())
    asyncio.run(run_optimized())
