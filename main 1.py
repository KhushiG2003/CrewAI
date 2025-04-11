#!/usr/bin/env python
import re
import sys
import os
import crew
from urllib.parse import quote_plus
from crew import DataProfiling
#from data_masking.masking_crew import DataMasking 
import streamlit as st
from crewai_tools import FileWriterTool, FileReadTool
from langchain_community.utilities.sql_database import SQLDatabase
from PIL import Image



# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information


# Fill columns with output
#cols[0].write("This is output in Column 1.This is output in Column 1.This is output in Column 1.This is output in Column 1.This is output in Column 1.")
#cols[1].write("This is output in Column 2.This is output in Column 2.This is output in Column 2.This is output in Column 2.This is output in Column 2.This is output in Column 2.")


def run(db_name,table_analysis=False, user_question=""):
    # Initialize the tool
    file_writer_tool = FileWriterTool()
    
    """
    Run the crew.
    """
    cols = st.columns([5, 5])  # Adjust the number for the desired number of columns
    inputs = {
        'database_name': f"{db_name}",
        'user_question': f"{user_question}"
    }
    print(inputs)
    crew = DataProfiling().crew(table_analysis)
    #print(crew.model_config)
    #print(crew)
    # Path to the folder containing the images
    image_folder = "images"
    for filename in os.listdir(image_folder):
        file_path = os.path.join(image_folder, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)

            
    results = crew.kickoff(inputs=inputs)
    # Display the final result
    result = f"## Here is the Final Result \n\n {results}"
    #st.session_state.messages.append({"role": "assistant", "content": result})
    #st.chat_message("assistant").write(result)
    # Write content to a file in a specified directory
    cols[1].write(result)
    # Extract file names ending with .png using regex


    # Get all .png files from the specified folder
    try:
        file_names = [f for f in os.listdir(image_folder) if f.endswith(".png")]
    except FileNotFoundError:
        st.error(f"The folder '{image_folder}' does not exist.")
        file_names = []

        
    print("filenames",file_names)
    if file_names:
        st.write("### Extracted File Names:")
        for file in file_names:
            cols[1].write(f"- {file}")
            file_path = os.path.join(image_folder, file)
            # Assuming the file is available locally for display
            try:
                cols[1].image(file_path, caption=file, use_container_width=True)
            except Exception as e:
                cols[1].write(f"Could not display `{file_path}`: {e}")
    else:
        cols[1].write("No file names found in the input string.")
    result = file_writer_tool._run(filename='profiling.txt', content = result, overwrite="True")

def run_data_masking(database_name):
    """
    Run the crew.
    """
    file_read_tool = FileReadTool()
    pii_info = file_read_tool._run(file_path='profiling.txt') 
    pii_info = "Database: bookdb:" + pii_info
    print(pii_info)

    cols = st.columns([5, 5])  # Adjust the number for the desired number of columns
    
    inputs = {
        'database_name' : f"{database_name}",
        'profiling_results': f"{pii_info}"
    }
    print(inputs)
    #crew = DataMasking().crew()
    #print(crew.model_config)
    #print(crew)
    results = crew.kickoff(inputs=inputs)
    # Display the final result
    result = f"## Here is the Final Result \n\n {results}"
    #st.session_state.messages.append({"role": "assistant", "content": result})
    #st.chat_message("assistant").write(result)
    cols[1].write(result)
    #st.write(result)

def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs"
    }
    try:
        DataProfiling().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        DataProfiling().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs"
    }
    try:
        DataProfiling().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")





if __name__ == "__main__" :
    # Streamlit UI setup
    im = Image.open("CAP2.png")
    st.set_page_config(layout="wide", initial_sidebar_state="collapsed", page_title="Test Data Framework - Data Profiling, PII Detection & Data Masking", page_icon=im)
    

    # Initialize session state
    if "db" not in st.session_state:
        st.session_state.db = None
    if "db_uri" not in st.session_state:
        st.session_state.db_uri = None
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Which Database would you like to explore?"}]

    # Sidebar: Database connection details
    st.sidebar.title("Database Connection")
    db_type = st.sidebar.selectbox("Select Database Type", ["MySQL", "MSSQL"])
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    server_name = st.sidebar.text_input("Server Name")
    database_name = st.sidebar.text_input("Database Name")

    # Button to validate the connection
    if st.sidebar.button("Test Connection"):
        if db_type and username and password and server_name and database_name:
            try:
                if db_type == "MySQL":
                    st.session_state.db_uri = f"mysql+pymysql://{quote_plus(username)}:{quote_plus(password)}@{server_name}:3306/{quote_plus(database_name)}"
                elif db_type == "MSSQL":
                    st.session_state.db_uri = f"mssql+pyodbc://{quote_plus(username)}:{quote_plus(password)}@{server_name}/{quote_plus(database_name)}?driver=ODBC+Driver+17+for+SQL+Server"
                print(st.session_state.db_uri)
                db = SQLDatabase.from_uri(database_uri=st.session_state.db_uri)    
                st.session_state.db = db
                st.success("Database connection successful!")
            except Exception as e:
                st.error(f"Database connection failed: {e}")
                st.session_state.db = None
        else:
            st.error("Please fill in all the database connection fields.")

    if st.session_state.db:
        with st.sidebar:
            st.subheader("Select an Operation")
            action = st.radio("Choose Action", ["Data Profiling", "Data Masking", "Table Analysis"], index=0, horizontal=True)

        # Display existing chat messages
    #    for msg in st.session_state.messages:
    #        st.chat_message(msg["role"]).write(msg["content"])

        # Handle user input
    #    if prompt := st.chat_input():
    #        st.session_state.messages.append({"role": "user", "content": prompt})
    #        st.chat_message("user").write(prompt)
            if action == "Table Analysis":
                user_question = st.text_area(label="Enter your query", value="e.g. : For the Table CUSTOMER ACCOUNT for all columns:\
                                                        a) Count of all records \
                                                        b) NULL values in each Column \
                                                        c) Duplicate values in each Column.")
                
        # Execute based on selected action
        if st.sidebar.button("Process"):
            if action == "Data Profiling":
                run(database_name, False)
           # elif action == "Data Masking":
           #     run_data_masking(database_name)
            elif action == "Table Analysis":
                # Multiselect widget
                run(database_name, True, user_question)
    else:
        st.info("Please validate the database connection to proceed.")
