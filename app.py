import streamlit as st
import sqlite3
from ddl_questions import ddl_questions
from dml_questions import dml_questions
from dql_questions import dql_questions
from tcl_questions import tcl_questions
from joins import joins_questions
from windows import window_questions
from cte import cte_questions
from triggers import trigger_questions
# from stored_procedures import stored_procedure_app
# Set up the SQLite database
conn = sqlite3.connect(':memory:')
cursor = conn.cursor()

# Create a sample table for testing
cursor.execute('''
    CREATE TABLE employees (
        id INTEGER PRIMARY KEY,
        name TEXT,
        department TEXT,
        salary REAL
    )
''')
conn.commit()

st.title("SQL Practice Website")

# Sidebar for navigation
category = st.sidebar.selectbox(
    "Select SQL Category",
    ["DDL", "DML", "DQL", "TCL", "JOINS", "WINDOW FUNCTION", "CTEs", "TRIGGERS"]
)

if category == "DDL":
    ddl_questions(conn, cursor)
elif category == "DML":
    dml_questions(conn, cursor)
elif category == "DQL":
    dql_questions(conn, cursor)
# elif category == "DCL":
#     dcl_questions(conn, cursor)
elif category == "TCL":
    tcl_questions(conn, cursor)
elif category == "JOINS":
    joins_questions(conn, cursor)
elif category == "WINDOW FUNCTION":
    window_questions(conn, cursor)
elif category == "CTEs":
    cte_questions(conn, cursor)
elif category == "TRIGGERS":
    trigger_questions(conn, cursor)
# elif category == "STORED PROCEDURES":
#     stored_procedure_app(conn, cursor)
# Add other categories as needed

conn.close()
