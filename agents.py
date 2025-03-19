from crewai import Agent,LLM
from tools import nl2sql

from dotenv import load_dotenv

load_dotenv()

import os

llm = LLM(
              model='gemini/gemini-2.0-flash',
              api_key=os.getenv("GOOGLE_API_KEY")
            )



# Agent to analyze the dbo_Employee table
table_researcher = Agent(
    role='Database Analyst',
    goal='Analyze the dbo_Employee table and provide insights.',
    verbose=True,
    memory=True,
    backstory=(
        "An expert in understanding SQLite databases, capable of analyzing table structures and extracting useful insights."
    ),
    tools=[nl2sql],
    allow_delegation=True,
    llm=llm
)

# Agent to insert dummy records into dbo_Employee table
crud_operator = Agent(
    role='Database Engineer',
    goal='Insert 5 dummy records into the dbo_Employee table.',
    verbose=True,
    memory=True,
    backstory=(
        "An expert in performing CRUD operations on SQLite databases, ensuring data integrity and consistency."
    ),
    tools=[nl2sql],
    allow_delegation=True,
    llm=llm
)