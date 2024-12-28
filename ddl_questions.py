import streamlit as st
import sqlite3
import pandas as pd

def ddl_questions(conn, cursor):
    st.header("SQL DDL Practice")
    cursor.execute("DROP TABLE IF EXISTS sales")
    cursor.execute("DROP TABLE IF EXISTS employees")
    cursor.execute("DROP TABLE IF EXISTS departments")
    
    questions = {
        "create_table": [
            {
                "question": "Create a table named 'employees' with columns: id (integer, primary key), name (varchar), age (integer), salary (decimal)",
                "solution": """
                    CREATE TABLE employees (
                        id INTEGER PRIMARY KEY,
                        name VARCHAR(100),
                        age INTEGER,
                        salary DECIMAL(10,2)
                    );
                """,
                "explanation": "Basic CREATE TABLE statement with different data types and a primary key constraint."
            },
            {
                "question": "Create a table 'departments' with columns: id (primary key), name (unique), location (not null)",
                "solution": """
                    CREATE TABLE departments (
                        id INTEGER PRIMARY KEY,
                        name VARCHAR(50) UNIQUE,
                        location VARCHAR(100) NOT NULL
                    );
                """,
                "explanation": "CREATE TABLE with UNIQUE and NOT NULL constraints."
            }
        ],
        "alter_table": [
            {
                "question": "Add a column 'email' to employees table",
                "solution": """
                    ALTER TABLE employees
                    ADD COLUMN email VARCHAR(100);
                """,
                "explanation": "ALTER TABLE to add a new column."
            },
            {
                "question": "Add a foreign key constraint to employees referencing departments",
                "solution": """
                    ALTER TABLE employees
                    ADD COLUMN department_id INTEGER
                    REFERENCES departments(id);
                """,
                "explanation": "ALTER TABLE to add a foreign key relationship."
            }
        ],
        "drop_table": [
            {
                "question": "Drop the employees table if it exists",
                "solution": """
                    DROP TABLE IF EXISTS employees;
                """,
                "explanation": "DROP TABLE with IF EXISTS clause to avoid errors."
            }
        ],
        "modify_constraints": [
            {
                "question": "Add a check constraint to ensure salary is positive",
                "solution": """
                    ALTER TABLE employees
                    ADD CONSTRAINT check_salary
                    CHECK (salary > 0);
                """,
                "explanation": "Adding a CHECK constraint to validate data."
            }
        ],
        "create_index": [
            {
                "question": "Create an index on employee name",
                "solution": """
                    CREATE INDEX idx_employee_name
                    ON employees(name);
                """,
                "explanation": "Creating an index to improve query performance."
            }
        ]
    }

    ddl_type = st.selectbox("Select DDL Operation:", 
                           list(questions.keys()), 
                           format_func=lambda x: x.replace('_', ' ').title())
    
    question_index = st.selectbox("Select Question:", 
                                range(1, len(questions[ddl_type]) + 1), 
                                format_func=lambda x: f"Question {x}")
    
    selected_question = questions[ddl_type][question_index - 1]

    st.subheader("Question:")
    st.write(selected_question["question"])
    
    user_query = st.text_area("Enter your SQL query:")
    
    if st.button("Submit"):
        try:
            cursor.execute(user_query)
            conn.commit()
            st.success("Query executed successfully!")
            
            # Show table structure after execution
            if "create" in user_query.lower() or "alter" in user_query.lower():
                cursor.execute("SELECT sql FROM sqlite_master WHERE type='table'")
                table_definitions = cursor.fetchall()
                st.write("Current Table Definitions:")
                for definition in table_definitions:
                    st.code(definition[0], language="sql")
                    
        except Exception as e:
            st.error(f"Error executing query: {str(e)}")
    
    if st.button("Show Solution", key="show_solution"):
        st.code(selected_question["solution"], language="sql")
        st.write("Explanation:")
        st.write(selected_question["explanation"])

def main():
    st.title("SQL DDL Practice App")
    conn = sqlite3.connect(':memory:', check_same_thread=False)
    cursor = conn.cursor()

    try:
        ddl_questions(conn, cursor)
    except sqlite3.Error as e:
        st.error(f"An error occurred: {e}")

    conn.close()

if __name__ == "__main__":
    main()
