from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai import LLM
from crewai_tools.tools import NL2SQLTool
from custom_handler import CustomHandler
import streamlit as st
from langchain_community.utilities.sql_database import SQLDatabase
from crewai_tools import tool
from langchain_community.tools.sql_database.tool import (
    InfoSQLDatabaseTool,
    ListSQLDatabaseTool,
    QuerySQLCheckerTool,
    QuerySQLDataBaseTool,
)
from langchain_openai.chat_models.azure import AzureChatOpenAI
 
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Literal
import os
import io
 
 
 
# Uncomment the following line to use an example of a custom tool
# from new_project.tools.custom_tool import MyCustomTool
 
# Check our tools documentations for more information on how to use them
# from crewai_tools import SerperDevTool
llm = LLM(
            model = "gpt-4o",
            base_url = "https://genaitcgazuregpt.openai.azure.com/",
            api_version = "2023-07-01-preview",
            api_key = "6202aa112d964a35aa3b08fe5d5f2700",
            azure=True,
        )
 
llm1 = AzureChatOpenAI(azure_endpoint="https://genaitcgazuregpt.openai.azure.com/",api_version="2023-07-01-preview",api_key="6202aa112d964a35aa3b08fe5d5f2700", model="gpt-4o",azure_deployment='gpt-4o',temperature=0)
 
 
db:SQLDatabase = None
 
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
 
@tool("check_sql")
def check_sql(sql_query: str,result_as_answer=True) -> str:
    """
    Use this tool to double check if your query is correct before executing it. Always use this
    tool before executing a query with `execute_sql`.
    """
    return QuerySQLCheckerTool(db=db, llm=llm1).invoke({"query": sql_query})
 
@tool('generate_chart')
def generate_chart(chart_type: Literal['scatter','line','bar'], data_json: str,  x_axis: str, y_axis: str, filename: str) -> str:
    """
    Generate a Seaborn chart based on input data and save it as an image file.
 
    In bar chart, prioritize passing string column as the y-axis.
 
    This function creates a chart using Seaborn and matplotlib, based on the specified
    chart type and input data. The resulting chart is saved as an image file.
 
    Parameters:
    -----------
    chart_type : Literal['scatter', 'line', 'bar']
        The type of chart to generate. Must be one of 'scatter', 'line', or 'bar'.
    data_json : str
        A JSON string containing the data to be plotted. The JSON should be structured
        such that it can be converted into a pandas DataFrame.
    filename : str
        The name of the file (including path if necessary) where the chart image will be saved.
    x_axis : str
        The name of the column in the data to be used for the x-axis.
    y_axis : str
        The name of the column in the data to be used for the y-axis.
 
    Returns:
    --------
    str
        A message confirming that the chart has been saved, including the filename.
 
    """
   
    # Convert JSON input to a pandas DataFrame
    data = json.loads(data_json)
    df = pd.DataFrame(data)
 
    # Create the Seaborn plot
    plt.figure(figsize=(10, 6))
    if chart_type == "scatter":
        sns.scatterplot(data=df, x=x_axis, y=y_axis)
    elif chart_type == "line":
        sns.lineplot(data=df, x=x_axis, y=y_axis)
    elif chart_type == "bar":
        sns.barplot(data=df, x=x_axis, y=y_axis)
    else:
        raise ValueError(f"Unsupported chart type: {chart_type}")
   
    # Set labels
    plt.xlabel(x_axis)
    plt.ylabel(y_axis)
    plt.title(f"{chart_type.capitalize()} Chart: {y_axis} vs {x_axis}")
   
    # Save the plot to the specified file
    plt.savefig("images/"+filename, format='png', dpi=300, bbox_inches='tight')
 
    # Save the plot to a BytesIO object for optional Streamlit display via st.image
    img_data = io.BytesIO()
    plt.savefig(img_data, format='png', dpi=300, bbox_inches='tight')
    #img_data.seek(0)
    #cols[0].image(img_data, caption=f"{chart_type.capitalize()} Chart: {y_axis} vs {x_axis}", use_column_width=True)
 
    # Close the plot
    plt.close()
 
    return f"Chart saved as {filename}"
 
# My initial parsing code using callback handler to print to app
def streamlit_callback(step_output):
    cols = st.columns([5, 5])  # Adjust the number for the desired number of columns
    # This function will be called after each step of the agent's execution
    cols[0].markdown("Step Completed ---")
    #st.markdown(f"{step_output}")
    #st.session_state.messages.append({"role": "assistant", "content": step_output.raw})
    #st.chat_message("assistant").write(step_output.raw)
    print("TASK OUTPUT",step_output.raw)
           
def streamlit_agent_callback(output):
    cols = st.columns([5, 5])  # Adjust the number for the desired number of columns
    print("Agent Output", output)
    if hasattr(output, '__dict__'):
        attributes = output.__dict__
        for key, value in attributes.items():
            if key in ['text']:
                cols[0].markdown((f"{key}: {value}"))
            print(f"{key}: {value}")
   
    cols[0].markdown("Agent Step Completed ---")
   
 
 
@CrewBase
class DataProfiling():
    """DataProfiling crew"""
 
    def __init__(self):
        """Initialize the DataProfiling class with a database URI."""
        #self.db_uri = db_uri
        global db
        #db = SQLDatabase.from_uri(database_uri=self.db_uri)
        db = st.session_state.db
    #nl2sql = NL2SQLTool(db_uri="mysql+pymysql://root:abc123@localhost:3306/")
   
    '''
    @agent
    def decomposer_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['decomposer_agent'],
            llm=llm,
            tools=[self.nl2sql], # Example of custom tool, loaded on the beginning of file
            verbose=True
        )
    '''
 
 
   
   
    #@agent
    def init(self,table_analysis):
 
        selector_agent = Agent(
            config=self.agents_config['selector_agent'],
            tools=[list_tables, tables_schema, execute_sql, check_sql,generate_chart],
            llm=llm,
            verbose=True,
            step_callback = streamlit_agent_callback
            )
 
        data_profiling_specialist_agent = Agent(
            config=self.agents_config['data_profiling_specialist_agent'],
            llm=llm,
            verbose=True,
            step_callback = streamlit_agent_callback
            )
 
        reporting_agent = Agent(
            config=self.agents_config['reporting_agent'],
            llm=llm,
            verbose=True,
            step_callback = streamlit_agent_callback
            )
 
            #chart_generation_agent = Agent(
            #  config=agents_config['chart_generation_agent'],
            #  allow_code_execution=True,
            #  llm=llm,
            #  verbose=True
            #)
 
 
            #decompose_question_task = Task(
            #  config=tasks_config['decompose_question_task'],
            #  agent=decomposer_agent
            #)
 
            # Creating Tasks
        table_analysis_task = Task(
            config=self.tasks_config['table_analysis_task'],
            agent=selector_agent,
            verbose=True,
            callback = streamlit_callback
            )
       
        chart_generation_task = Task(
            config=self.tasks_config['chart_generation_task'],
            agent=selector_agent,
            verbose=True,
            callback = streamlit_callback
            )
       
        select_relevant_schema_task = Task(
            config=self.tasks_config['select_relevant_schema_task'],
            agent=selector_agent,
            verbose=True,
            callback = streamlit_callback
            )
 
        select_relevant_column_values = Task(
            config=self.tasks_config['select_relevant_column_values'],
            agent=selector_agent
            )
 
        data_profiling_task = Task(
            config=self.tasks_config['data_profiling_task'],
            agent=data_profiling_specialist_agent,
            context=[select_relevant_schema_task,select_relevant_column_values],
            callback = streamlit_callback
               
            )
 
 
        pii_sensitivity_risk_assessment_report_generation_task = Task(
            config=self.tasks_config['pii_sensitivity_risk_assessment_report_generation_task'],
            agent=reporting_agent,
            context=[data_profiling_task],
            callback = streamlit_callback
            )
 
 
        compliance_alignment_report_task = Task(
            config=self.tasks_config['compliance_alignment_report_task'],
            agent=reporting_agent,
            context=[data_profiling_task],
            callback = streamlit_callback
            )
 
        final_report_assembly = Task(
            config=self.tasks_config['final_report_assembly'],
            agent=reporting_agent,
            context=[select_relevant_column_values,data_profiling_task],
            callback = streamlit_callback
            )
 
 
            #refiner_agent = Agent(
            #  config=agents_config['refiner_agent'],
            #  llm=llm,
            #  verbose=True
            #)
 
            #refine_sql_task = Task(
            #  config=tasks_config['refine_sql_task'],
            #  agent=refiner_agent
            #)
 
        if table_analysis:
            # Creating Crew
            date_profiling_crew = Crew(
                agents=[
                    selector_agent
                ],
                tasks=[
                    table_analysis_task
                    #chart_generation_task                  
                ],
                verbose=True,
                )
            return date_profiling_crew
       
        else:  
            # Creating Crew
            date_profiling_crew = Crew(
                agents=[
                    selector_agent,
                    data_profiling_specialist_agent,
                    reporting_agent
                ],
                tasks=[
                    select_relevant_schema_task,
                    data_profiling_task,
                    final_report_assembly
                ],
                verbose=True,
                )
            return date_profiling_crew
       
 
 
    @crew
    def crew(self,table_analysis) -> Crew:
        """Creates the DataProfiling crew"""
 
        '''
        sel_agent = self.selector_agent()
        data_profiling_agent = self.data_profiling_specialist_agent()
        rep_agent = self.reporting_agent()
 
        sel_rel_schema_task = self.select_relevant_schema_task()
        profiling_task = self.data_profiling_task()
        pii_assessment_task = self.pii_sensitivity_risk_assessment_report_generation_task()
        compliance_task = self.compliance_alignment_report_task()
        final_report_task = self.final_report_assembly()
       
        return Crew(
 
            agents=[sel_agent, data_profiling_agent, rep_agent],
            tasks=[sel_rel_schema_task, profiling_task, pii_assessment_task, compliance_task, final_report_task],  
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
        '''
        return self.init(table_analysis)    