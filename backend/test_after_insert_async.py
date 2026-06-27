import asyncio
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import event

Base = declarative_base()

class Dummy(Base):
    __tablename__ = 'dummies'
    id = Column(Integer, primary_key=True)
    name = Column(String)

def after_insert_listener(mapper, connection, target):
    # we need to ensure this works in async engine
    print(f"Sync listener called for: {target.name}")
    try:
        loop = asyncio.get_running_loop()
        print("Got loop!")
    except RuntimeError:
        print("No loop!")

event.listens_for(Dummy, 'after_insert')(after_insert_listener)

async def main():
    engine = create_async_engine('sqlite+aiosqlite:///:memory:', echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    Session = async_sessionmaker(engine)
    async with Session() as session:
        session.add(Dummy(name="test_async"))
        await session.commit()

asyncio.run(main())
