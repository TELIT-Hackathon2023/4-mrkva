from fastapi import (
    FastAPI,
    HTTPException,
    Depends
)
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    Integer,
    String,
    Text,
    Boolean
)

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

from pydantic import BaseModel
from scraper import wikiScraper

database = "postgresql://postgres:MundianToBachKe@postgres:5432/telit_hack_db"
engine = create_engine(database)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
metadata = MetaData()
Base = declarative_base()


class FandomWikiRequest(BaseModel):
    url: str


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


def create_dynamic_table(table_name, columns):
    return Table(table_name, metadata, *columns)


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


@app.post("/fandom_wikis/add")
def post_fandom_wiki(request: FandomWikiRequest, db: Session = Depends(get_db)):
    try:
        url = request.url
        page_tree = wikiScraper.scrape_page_tree(url)
        table_name = wikiScraper.get_page_title(url)

        table = Tables(
            human_readable_name=table_name,
            database_table_name=table_name,
            description=f"Table for {table_name} fandom wiki",
            is_template=False
        )

        db.add(table)

        columns = [
            Column('id', Integer, primary_key=True),
            Column('html_tag', String),
            Column('contents', Text),
            Column('link', String),
        ]

        # Create a dynamic table
        dynamic_table = create_dynamic_table(table_name, columns)

        # Create the table in the database
        metadata.create_all(engine)

        for element in page_tree:
            for each in element:
                # Insert data into the dynamically created table
                db.execute(
                    dynamic_table.insert(),
                    {
                        "html_tag": each.html_tag,
                        "contents": each.contents,
                        "link": each.link
                    },
                )

        db.commit()

        return {"message": f"Table {table_name} created and rows inserted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error inserting rows: {str(e)}")


@app.get("/fandom_wikis/{table_name}")
def get_fandom_wiki(table_name: str, db: Session = Depends(get_db)):
    table = db.query(Tables).filter(Tables.database_table_name == table_name).first()
    if table is None:
        raise HTTPException(status_code=404, detail="Table not found")
    return {"id": table.id,
            "human_readable_name": table.human_readable_name,
            "database_table_name": table.database_table_name,
            "description": table.description,
            "is_template": table.is_template
            }


@app.get("/fandom_wikis")
def get_fandom_wikis(db: Session = Depends(get_db)):
    tables = db.query(Tables).all()
    return tables


@app.get("/fandom_wikis/{table_name}/contents")
def get_fandom_wiki_contents(table_name: str, db: Session = Depends(get_db)):
    dynamic_table = Table(table_name, metadata, autoload=True, autoload_with=engine)
    if dynamic_table is None:
        raise HTTPException(status_code=404, detail="Table not found")
    rows = db.query(dynamic_table).all()
    return [
        {
            "id": row.id,
            "html_tag": row.html_tag,
            "contents": row.contents,
            "link": row.link
        }
        for row in rows
    ]


@app.get("/fandom_wikis/{table_name}/contents/{searched_keyword}")
def get_fandom_wiki_contents_searched(
        table_name: str,
        searched_keyword: str,
        db: Session = Depends(get_db)
):
    dynamic_table = Table(table_name, metadata, autoload=True, autoload_with=engine)
    if dynamic_table is None:
        raise HTTPException(status_code=404, detail="Table not found")
    rows = db.query(dynamic_table).all()
    return [
        {
            "id": row.id,
            "html_tag": row.html_tag,
            "contents": row.contents,
            "link": row.link
        }
        for row in rows
        if searched_keyword in row.contents
    ]
