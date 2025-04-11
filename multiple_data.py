## ****** For genrating data for multiple tables ******

import csv
import os
import pyodbc
import pandas as pd
from crewai import Crew, Task, Agent

from dotenv import load_dotenv
load_dotenv()


# Configure LiteLLM correctly
from crewai import LLM
# llm = LLM(
#             model = "gpt-4o",
#             base_url = "https://genaitcgazuregpt.openai.azure.com/",
#             api_version = "2023-07-01-preview",
#             api_key = "6202aa112d964a35aa3b08fe5d5f2700",
#             azure=True,
#         )

llm = LLM( model='gemini/gemini-2.0-flash',
           api_key=os.getenv("GOOGLE_API_KEY")
            )


# Establish the connection
# db_name = 'OneClickDB'
db_name = 'GenAICreditcard'
conn = pyodbc.connect("DRIVER={ODBC Driver 17 for SQL Server};SERVER=INBLRVM78094602;DATABASE="+db_name+";UID=test;PWD=Capgemini@1234")


#List of tables
tables = ["ADDRESS","INDIVIDUAL_CARDHOLDER"]

#Loop for selecting table for executing select query

df_list = []
schema_list = []
data_summary_list = []

for table in tables:
    query = f"Select * from {table}"
    # query = "SELECT fk.name AS FK_Name, tp.name AS FK_Table, cp.name AS FK_Column, tr.name AS PK_Table, cr.name AS PK_Column FROM sys.foreign_keys AS fk INNER JOIN sys.foreign_key_columns AS fkc ON fk.object_id = fkc.constraint_object_id INNER JOIN sys.tables AS tp ON fkc.parent_object_id = tp.object_id INNER JOIN sys.columns AS cp ON fkc.parent_object_id = cp.object_id AND fkc.parent_column_id = cp.column_id INNER JOIN sys.tables AS tr ON fkc.referenced_object_id = tr.object_id INNER JOIN sys.columns AS cr ON fkc.referenced_object_id = cr.object_id AND fkc.referenced_column_id = cr.column_id"
    
    
    # constraint_query = f""" SELECT col.name AS ColumnName, typ.name AS DataType, col.max_length, col.is_nullable, col.is_identity, CASE WHEN pk.colid IS NOT NULL THEN 1 ELSE 0 END AS IsPrimaryKey FROM sys.columns col INNER JOIN sys.types typ ON col.user_type_id = typ.user_type_id INNER JOIN sys.objects obj ON col.object_id = obj.object_id LEFT JOIN (SELECT ic.object_id, ic.column_id AS colid FROM sys.indexes i INNER JOIN sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id WHERE i.is_primary_key = 1) pk ON col.object_id = pk.object_id AND col.column_id = pk.colid WHERE obj.name = '{table}' """


    df = pd.read_sql(query, conn)
    print("-------------------------")
    # print(df.head(20).to_dict(orient='records'))
    print(df)

    # -------------------------------------------------------------------------------

    # constraint_df = pd.read_sql(constraint_query, conn)
    # print("--------------------------------------")
    # print(constraint_df)


    # constraints = {}
    # for _, row in constraint_df.iterrows():
    #     constraints[row["ColumnName"]] = {
    #         "data_type": row["DataType"],
    #         "max_length": row["max_length"],
    #         "nullable": bool(row["is_nullable"]),
    #         "primary_key": bool(row["IsPrimaryKey"]),
    #         "autoincrement": bool(row["is_identity"])
    #     }

    # print(constraints)


    # --------------------------------------------------------------------------------

    # Analyze the schema and data
    schema = df.dtypes.to_dict() 
    # schema = constraint_df.dtypes.to_dict()
    data_summary = df.describe(include='all').to_dict()  # Include all columns in the summary
    # data_summary = constraint_df.describe(include='all').to_dict()  # Include all columns in the summary



    print("--------------------------------------------------")
    print(f"Data of table {table}")
    print(df.head(20))
    # print(constraint_df.head(20))

    print("--------------------------------------------------")
    print(f"Schema of table {table}:")
    print(schema)
    
    print("--------------------------------------------------")    
    print(f"Data summary of table {table}:")
    print(data_summary)

    # df_list.append(df.head(20).to_dict(orient='records'))
    df_list.append(df.head(20))
    # df_list.append(constraint_df.head(20))
    schema_list.append(schema)
    data_summary_list.append(data_summary)

    # print("-------------------------------------------------------------")
    # print(df.head(20).to_dict(orient='records'))





# Define the number of records to generate
num_records = 100  # Specify the number of records you want to generate

all_data = []

# Loop through tables to generate data for each one
for table, schema, data_summary, df in zip(tables, schema_list, data_summary_list, df_list):

    # Define an AI Agent
    researcher = Agent(
        role="DataGeneratorAgent",
        goal=f"Analyze data and schema of the given table and generate exactly {num_records} new records",
        backstory="An expert in data generation using GPT models.",
        verbose=True,
        llm=llm
    )

    # data_summary=pd.DataFrame(data_summary).transpose()
    # data_summary.to_csv('data_summary.csv', index=True)



    # Define a Task
    task = Task(
        description=f"Generate new testing data for {table} using schema, data summary, and sample records from {tables}",
        agent=researcher,
        context=[
            {
                "description": "Schema of the SQL table",
                "expected_output": "A detailed schema of the SQL table",
                "schema": schema
            },
            {
                "description": "Data summary of the SQL table",
                "expected_output": "A statistical summary of the data in the SQL table",
                "data_summary": data_summary
            },

            {
                "description": "Use all columns available in schema and generate Number of records to generate",
                "expected_output": f"Generate exactly {num_records} new records for {df.columns}",
                "num_records": num_records
            },
            
            {   
                "description": "Sample records for analysis",
                "expected_output": "Use this data to understand the type of data to generate",
                # "sample_records": df.head(20).to_dict(orient='records')
                "sample_records": df.to_dict(orient='records')

                # "sample_records": constraint_df.to_dict(orient='records')

                # "sample_records": df_list
            }
        ],


    
        expected_output=f"Generate exactly {num_records} new records for {df.columns} based on the given schema and data for analysis, then store it into a CSV."
    )
    # Create a Crew and Run
    crew = Crew(agents=[researcher], tasks=[task], verbose=True)
    result = crew.kickoff()

    import io
    csv_data = str(result).strip('```csv\n').strip('```')

    # Convert the CSV data to a DataFrame
    data = pd.read_csv(io.StringIO(csv_data))


    data.to_csv(f"{table}.csv", index=False)

    print("\n📝 Final Result:\n", result)



    # all_data.append(data)

# final_data = pd.concat(all_data, ignore_index=True)

# Save the DataFrame to a CSV file
# final_data.to_csv("testcrewai_data_modified.csv", index=False)

# print("\n📝 Final Result:\n", result)

