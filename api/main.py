from fastapi import (
    FastAPI,
    HTTPException,
    Depends,
    Request
)
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    Integer,
    String,
    Date,
    Text,
    Numeric,
    DateTime,
    func,
    Boolean
)

from sqlalchemy.sql import func

from sqlalchemy.orm import (
    sessionmaker,
    declarative_base,
    Session
)
from tenacity import (
    retry,
    wait_fixed,
    stop_after_attempt
)

database = "postgresql://postgres:MundianToBachKe@postgres:5432/telit_hack_db"
engine = create_engine(database)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Tables(Base):
    __tablename__ = "tables"
    id = Column(Integer, primary_key=True, index=True)
    human_readable_name = Column(String, index=True)
    database_table_name = Column(String, index=True)
    description = Column(String, nullable=True)
    is_template = Column(Boolean, default=False)


app = FastAPI()


# Connect to Database Engine
# Retry every 10 seconds, stop after 3 attempts
@retry(wait=wait_fixed(10), stop=stop_after_attempt(3))
async def connect_to_db():
    try:
        engine.connect()
    except Exception as e:
        print("Error while connecting to the database:", e)
        raise e


# Initialize tables in the database and prepare for communication
# Executes after connect_to_db() function
@app.on_event("startup")
async def startup():
    # Connect to the database
    try:
        await connect_to_db()
    except Exception:
        print("Failed to connect to the database after several attempts.")

    # Create tables
    Base.metadata.create_all(bind=engine)


# Close connection to the database
@app.on_event("shutdown")
async def shutdown():
    await engine.dispose()


# Basic message
@app.get("/")
async def root():
    return {"message": "Please make requests using provided API documentation !"}




