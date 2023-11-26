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
    Boolean,
    text
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

import scraper.wikiScraper as wikiScraper

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


class PageTreeData(Base):
    id = Column(Integer, primary_key=True, index=True)
    html_tag = Column(String)
    contents = Column(String)
    link = Column(String)


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


@app.post("/fandom_wiki/add/{fandom_url}")
def post_fandom_wiki(fandom_url: str, db: Session = Depends(get_db)):
    try:
        page_tree = wikiScraper.scrape_page_tree(fandom_url)

        table_name = fandom_url.lower().replace(" ", "_")
        table_definition = f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id SERIAL PRIMARY KEY,
                    html_tag VARCHAR(255),
                    contents VARCHAR(255),
                    link VARCHAR(255),
                )
            """
        with engine.connect() as connection:
            connection.execute(text(table_definition))

        for element in page_tree.contents:
            db_element = PageTreeData(**element.dict(), table_name=table_name)
            db.add(db_element)
        db.commit()

        return {"message": f"Table {table_name} created and rows inserted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error inserting rows: {str(e)}")