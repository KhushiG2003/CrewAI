from crewai_tools import NL2SQLTool

# psycopg2 was installed to run this example with PostgreSQL
nl2sql = NL2SQLTool(db_uri="sqlite:///database.db")