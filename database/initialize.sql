/*

    Initialize the database with the following templates to be used by the generative API

*/


CREATE TABLE IF NOT EXISTS element_template (
    id serial PRIMARY KEY,
    html_tag varchar(255) NOT NULL,
    contents text NOT NULL,
    link varchar(255) DEFAULT NULL,
    child_of int REFERENCES element_template(id)
);

CREATE TABLE IF NOT EXISTS tables (
    id serial PRIMARY KEY,
    human_readable_name varchar(255) NOT NULL,
    database_table_name varchar(255) NOT NULL,
    description text,
    is_template boolean DEFAULT false
);

/*
Will be filled by FastAPI !!! Now omitted ...

-- Create the trigger function
CREATE OR REPLACE FUNCTION add_table ()
RETURNS TRIGGER AS $$
BEGIN
    -- Insert a new entry into table when we create a new table
    IF TG_OP = 'CREATE' THEN
        INSERT INTO table_metadata (human_readable_name, database_table_name, description, is_template)
        VALUES (TG_TABLE_NAME, TG_TABLE_NAME, NULL, false);
    END IF;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Create the trigger
CREATE TRIGGER table_created
AFTER CREATE ON SCHEMA public
FOR EACH STATEMENT
EXECUTE FUNCTION add_table();

*/