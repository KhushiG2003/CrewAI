from crewai import Crew, Task, Agent
import sqlite3

# Define the connection string
# connection_string = (
#     'DRIVER={ODBC Driver 17 for SQL Server};'
#     'SERVER=INBLRVM7890462;'
#     'DATABASE=Toscadisource;'
#     'UID=test;'
#     'PWD=Capgemini@1234'
# )

# Connect to the database
connection = sqlite3.connect("database.db")

# Create a cursor object
cursor = connection.cursor()

# Fetch the schema of the existing Employees table
# Create schema (SQLite doesn't support CREATE SCHEMA, but we simulate it using a prefix)
# schema = 'dbo'

# ## Create Employee table
# # cursor.execute(f'''
# #     CREATE TABLE IF NOT EXISTS {schema}_Employee (
# #         EmployeeID INTEGER PRIMARY KEY AUTOINCREMENT,
# #         FirstName TEXT NOT NULL,
# #         LastName TEXT NOT NULL,
# #         Email TEXT UNIQUE NOT NULL,
# #         Salary REAL CHECK(Salary >= 0),
# #         HireDate TEXT DEFAULT CURRENT_TIMESTAMP
# #     )
# # ''')

# # Insert 5 records
# employees = [
#     ('John', 'Doe', 'john.doe@example.com', 60000),
#     ('Jane', 'Smith', 'jane.smith@example.com', 65000),
#     ('Mike', 'Johnson', 'mike.johnson@example.com', 55000),
#     ('Emily', 'Davis', 'emily.davis@example.com', 70000),
#     ('Robert', 'Brown', 'robert.brown@example.com', 62000)
# ]

# cursor.executemany(f'''
#     INSERT INTO {schema}_Employee (FirstName, LastName, Email, Salary)
#     VALUES (?, ?, ?, ?)
# ''', employees)

print(cursor.execute("SELECT name FROM sqlite_master WHERE type='table'"))

# Commit and close connection
connection.commit()

# cursor.execute("SELECT * FROM dbo.Employees WHERE 1=0")
# reference_schema = cursor.description

# # Create a new table with the same schema
# create_table_query = "CREATE TABLE new_EmployeesData ("
# for column in reference_schema:
#     column_name = column[0]
#     column_type = column[1]

#     if column_type == pyodbc.SQL_INTEGER:
#         column_type = "INT"
#     elif column_type == pyodbc.SQL_VARCHAR:
#         column_type = "VARCHAR(50)"
#     elif column_type == pyodbc.SQL_FLOAT:
#         column_type = "FLOAT"
#     elif column_type == pyodbc.SQL_TYPE_TIMESTAMP:
#         column_type = "DATETIME"
#     elif column_type == pyodbc.SQL_BIT:
#         column_type = "BIT"
#     else:
#         column_type = "VARCHAR(50)"  # Default to VARCHAR for unknown types

#     create_table_query += f"{column_name} {column_type}, "

# create_table_query = create_table_query.rstrip(", ") + ")"
# cursor.execute(create_table_query)

# # Fetch data from the existing Employees table
# cursor.execute("SELECT * FROM dbo.Employees")
# existing_data = cursor.fetchall()

# # Define the agent task to generate new data
# def generate_new_data(existing_row):
#     new_row = []
#     for value in existing_row:
#         if isinstance(value, int):  # Example transformation: increment integer values by 1000
#             new_row.append(value + 1000)
#         elif isinstance(value, str):  # Example transformation: append " Jr." to string values
#             new_row.append(value + " Jr.")
#         else:
#             new_row.append(value)  # Keep other types of values unchanged
#     return tuple(new_row)


# # Create tasks for the agent
# tasks = [
#     Task(
#         func=generate_new_data,
#         args=(row,),
#         description="Generate new data by transforming existing data",
#         expected_output="Tuple with transformed data"
#     ) 
#     for row in existing_data
# ]

# # Create a Crew agent with required fields
# agent = Agent(
#     tasks=tasks,
#     role="Data Transformer",
#     goal="Generate new employee data based on existing data",
#     backstory="An agent designed to transform existing employee data for new table creation."
# )

# # Create a Crew instance with the agent
# crew = Crew(agents=[agent])

# # Execute the tasks and collect the results
# new_data = crew.kickoff()

# # Debugging: Print the outputs of each task
# print("Task Outputs:")
# for output in new_data:
#     print(output)

# # Insert new data into the new table
# insert_query = f"INSERT INTO new_1_EmployeesData ({', '.join([column[0] for column in reference_schema])}) VALUES ({', '.join(['?' for _ in reference_schema])})"
# cursor.executemany(insert_query, new_data)

# # Commit the transaction
# connection.commit()


# # Verify the data
# cursor.execute("SELECT * FROM new_EmployeesData")
# result = cursor.fetchall()
# for row in result:
#     print(row)

# Close the connection
connection.close()