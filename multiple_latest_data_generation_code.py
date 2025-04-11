from crewai import Agent, Crew, Task, LLM
from crewai.tools import tool
from langchain_community.utilities.sql_database import SQLDatabase
from urllib.parse import quote_plus
from langchain_community.tools.sql_database.tool import (
    InfoSQLDatabaseTool,
    ListSQLDatabaseTool,
    QuerySQLCheckerTool,
    QuerySQLDataBaseTool,
)
import io
import pandas as pd

server = "inblrvm78094602"
database = "GenAICreditcard"
username = "Test"
password = "Capgemini@1234"

db_uri = f"mssql+pyodbc://{quote_plus(username)}:{quote_plus(password)}@{server}/{quote_plus(database)}?driver=ODBC+Driver+17+for+SQL+Server"

db = SQLDatabase.from_uri(database_uri=db_uri)


@tool("list_tables")
def list_tables(result_as_answer=True) -> str:
    """List the available tables in the database"""
    return ListSQLDatabaseTool(db=db).invoke("")

@tool("tables_schema")
def tables_schema(tables: str,result_as_answer=True) -> str:
    """
    Input is a comma-separated list of tables, output is the schema including primary key and foriegn key information. Do NOT get any sample rows.
    Be sure that the tables actually exist by calling `list_tables` first!
    Example Input: table1, table2, table3
    """
    tool = InfoSQLDatabaseTool(db=db)
    return tool.invoke(tables)
 
@tool("execute_sql")
def execute_sql(sql_query: str,result_as_answer=True) -> str:
    """Execute a SQL query against the database. Returns the result"""
    return QuerySQLDataBaseTool(db=db).invoke(sql_query)
    

# Configure LiteLLM correctly

llm = LLM(
            model = "gpt-4o",
            base_url = "https://genaitcgazuregpt.openai.azure.com/",
            api_version = "2023-07-01-preview",
            api_key = "6202aa112d964a35aa3b08fe5d5f2700",
            azure=True,
        )

database_operator_agent = Agent(
    role = "DatabaseOperatorAgent",
    goal = "Extract data and schema of the {table_name} table. Understand the primary and foreign key relationships and constraints.",
    backstory = '''An expert in database processing tasks.
                   You are skilled in understanding database relationships.
                   Use `list_tables` to find available tables.
                   Use `tables_schema` to understand the metadata and keys for the table columns.
                   Use `execute_sql` to execute queries against the database.''',
    verbose = True,
    tools = [list_tables, tables_schema, execute_sql],
    llm = llm,
)
                                        
# Define an AI Agent
data_generator_agent = Agent(
    role = "DataGeneratorAgent",
    goal = "If the table has foreign keys, ensure that the columns generate values from primary key values in another table. Generate exactly {num_records} new records.",
    backstory = '''An expert in data generation using GPT models.
                   Use `execute_sql` to execute queries against the database.''',
    verbose = True,
    llm = llm
)

understand_table_task = Task(
    description = "Extract schema, columns, keys, and data from the table. Provide an understanding of the relationships between tables.",
    agent = database_operator_agent,
    expected_output = '''Provide details about the keys present in the table. If there are foreign keys, specify the source table.
    Describe the type of data each column contains and include data from the table. Additionally, 
    extract data from the parent table to generate values for the foreign key columns.'''
)

print("----")

# Define a Task
data_generation_task = Task(
    description='''Generate new testing data for all the given columns using schema, data summary, and records provided for analysis.
    When generating data, if the table has foreign keys, ensure you extract IDs from the parent table and use those IDs for the foreign key column values.''',
    agent=data_generator_agent,
    context=[understand_table_task],
    expected_output="Generate exactly {num_records} new records for all table columns based on the table schema. Ensure that foreign key values in the child table match existing primary key values in the parent table to maintain referential integrity. give output in csv format."
)

tables = ["ADDRESS","INDIVIDUAL_CARDHOLDER"]
# Define the number of records to generate
num_records = 50  # Specify the number of records you want to generate

for table_name in tables:
    # Create a Crew and Run
    crew = Crew(agents=[database_operator_agent,data_generator_agent], 
                tasks=[understand_table_task,data_generation_task], 
                # process=Process.sequential,
                # planning=True,
                verbose=True
            )
    result = crew.kickoff(inputs={'table_name':table_name, 'num_records':num_records})

    lines = str(result).strip().split('\n')
    csv_lines = [line for line in lines if ',' in line]

    clean_csv = "\n".join(csv_lines)


    # Convert the CSV data to a DataFrame
    data = pd.read_csv(io.StringIO(clean_csv))

    # Save the DataFrame to a CSV file
    data.to_csv("latest_individual_card_data.csv", index=False)

    print("\nFinal Result:\n", result)