import asyncio
from sqlalchemy import event, Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class Dummy(Base):
    __tablename__ = 'dummies'
    id = Column(Integer, primary_key=True)
    name = Column(String)

@event.listens_for(Dummy, "after_insert")
def receive_after_insert(mapper, connection, target):
    print(f"Inserted: {target.name}")

engine = create_engine('sqlite:///:memory:', echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def main():
    session = Session()
    d = Dummy(name="test")
    session.add(d)
    session.commit()

main()
