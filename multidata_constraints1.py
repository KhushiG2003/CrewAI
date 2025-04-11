import os
import pyodbc
import pandas as pd
import io
from dotenv import load_dotenv
from crewai import Crew, Agent, Task, LLM

# Load environment variables
load_dotenv()

# Initialize LLM (using Gemini)
llm = LLM(
    model='gemini/gemini-2.0-flash',
    api_key=os.getenv("GOOGLE_API_KEY")
)

# Connect to SQL Server
db_name = 'GenAICreditcard'
conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    f"SERVER=INBLRVM78094602;DATABASE={db_name};UID=test;PWD=Capgemini@1234"
)

# Tables to process
tables = ["ADDRESS", "INDIVIDUAL_CARDHOLDER"]

# Number of records to generate
num_records = 100

for table in tables:
    # Step 1: Load sample data
    df = pd.read_sql(f"SELECT * FROM {table}", conn)
    sample_data = df.head(20).to_dict(orient="records")

    # Step 2: Infer schema from df.dtypes and create manual schema prompt
    column_schema_prompt = "\n".join(
        [f"{col}: {str(dtype)}" for col, dtype in df.dtypes.items()]
    )
    column_names = list(df.columns)

    # ---------------- AGENT 1: DATA EXTRACTOR ----------------
    extractor = Agent(
        role="DataExtractorAgent",
        goal="Extract data patterns and constraints for synthetic generation",
        backstory="An expert data analyst skilled in identifying column-level data patterns and business rules from raw data.",
        verbose=True,
        llm=llm
    )

    extract_task = Task(
        description=f"""You are given 20 sample records from the SQL table: {table}.
            Do NOT infer or rename schema — column names must stay exactly as provided.

            Analyze this data and return for each column:
            - Value types (e.g., email, date, phone, zip, ID)
            - Possible patterns (e.g., string length, format, prefixes, ranges)
            - Whether the column is likely a Primary Key (based on uniqueness in the sample)
            - If any columns look like a Foreign Key (e.g., `customer_id` matching another table’s PK)

            Only infer value constraints. Do not rename or restructure the schema.

            Column names and types:
            {column_schema_prompt}
            """,
                        # - Uniqueness or nullable behavior (optional) 

        agent=extractor,
        context=[
            {
                "description": "Sample records from SQL table",
                "expected_output": "List of records used for pattern inference",
                "sample_records": sample_data
            }
        ],
        expected_output="JSON format describing patterns/constraints for each column (match column names exactly)."
    )

    # ---------------- AGENT 2: DATA GENERATOR ----------------
    generator = Agent(
        role="DataGeneratorAgent",
        goal="Generate synthetic tabular data matching column names and structure exactly",
        backstory="A master at generating structured test data from JSON-defined rules and table schema.",
        verbose=True,
        llm=llm
    )

    generate_task = Task(
        description=f"""Generate {num_records} synthetic records for the SQL table '{table}'.

            You must:
            - Use the exact column names and order (no renaming or reordering).
            - Use the following schema:
            {column_schema_prompt}
            - Use the patterns and constraints inferred by the previous agent.
            - Ensure final output is in **CSV format with headers**.
            - Maintain realistic but synthetic values.

            Important:
            - The output must be directly usable as CSV with these exact columns:
            {', '.join(column_names)}
            """,
        agent=generator,
        context=[extract_task],
        expected_output="CSV formatted string with headers and synthetic rows."
    )

    # Run agents via Crew
    crew = Crew(agents=[extractor, generator], tasks=[extract_task, generate_task], verbose=True)
    result = crew.kickoff()

    # Parse result and save
    csv_data = str(result).strip('```csv\n').strip('```')
    generated_df = pd.read_csv(io.StringIO(csv_data), engine='python')

    # Force correct column order
    generated_df = generated_df[column_names]

    # Save to CSV
    generated_df.to_csv(f"{table}_generated.csv", index=False)
    print(f"✅ Data for table '{table}' saved to {table}_generated.csv")
