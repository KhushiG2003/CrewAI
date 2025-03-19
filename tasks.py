from crewai import Task
from tools import nl2sql
from agents import table_researcher, crud_operator

# Task to analyze the dbo_Employee table
research_task = Task(
    description=(
        "Analyze the structure and data of the dbo_Employee table. "
        "Identify key patterns and insights from the stored employee records."
    ),
    expected_output='A detailed report on the structure, trends, and anomalies found in the dbo_Employee table.',
    tools=[nl2sql],
    agent=table_researcher,
)

# Task to insert dummy records into the dbo_Employee table
write_task = Task(
    description=(
        "Insert 5 dummy employee records into the dbo_Employee table. "
        "Ensure data is structured correctly and adheres to database constraints."
    ),
    expected_output='Confirmation message after inserting 5 dummy employee records.',
    tools=[nl2sql],
    agent=crud_operator,
    async_execution=False,
)