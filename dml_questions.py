import streamlit as st
import sqlite3
import pandas as pd

def dml_questions(conn, cursor):
    st.header("SQL DML Practice")
    
    # Drop existing tables
    cursor.execute("DROP TABLE IF EXISTS employees")
    cursor.execute("DROP TABLE IF EXISTS departments")
    
    # Create tables
    cursor.execute("""
        CREATE TABLE employees (
            id INTEGER PRIMARY KEY,
            name TEXT,
            department_id INTEGER,
            salary DECIMAL(10,2),
            hire_date DATE
        )
    """)
    
    cursor.execute("""
        CREATE TABLE departments (
            id INTEGER PRIMARY KEY,
            name TEXT,
            location TEXT,
            budget DECIMAL(10,2)
        )
    """)
    
    # Insert initial data
    cursor.executemany("INSERT INTO departments VALUES (?, ?, ?, ?)",
        [(1, 'IT', 'New York', 500000),
         (2, 'HR', 'London', 300000),
         (3, 'Sales', 'Tokyo', 400000)])
    
    cursor.executemany("INSERT INTO employees VALUES (?, ?, ?, ?, ?)",
        [(1, 'John', 1, 60000, '2023-01-01'),
         (2, 'Alice', 2, 55000, '2023-02-01'),
         (3, 'Bob', 1, 65000, '2023-01-15')])
    
    conn.commit()

    # Display tables
    st.subheader("Available Tables:")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Employees Table**")
        cursor.execute("SELECT * FROM employees")
        df = pd.DataFrame(cursor.fetchall(), 
                         columns=['id', 'name', 'department_id', 'salary', 'hire_date'])
        st.dataframe(df)
    
    with col2:
        st.write("**Departments Table**")
        cursor.execute("SELECT * FROM departments")
        df = pd.DataFrame(cursor.fetchall(), 
                         columns=['id', 'name', 'location', 'budget'])
        st.dataframe(df)

    st.divider()

    questions = {
        "insert": [
            {
                "question": "Insert a new employee",
                "solution": """
                    INSERT INTO employees (name, department_id, salary, hire_date)
                    VALUES ('Charlie', 2, 58000, '2024-01-01');
                """,
                "explanation": "Basic INSERT statement to add a new employee record."
            },
            {
                "question": "Insert multiple employees in one statement",
                "solution": """
                    INSERT INTO employees (name, department_id, salary, hire_date)
                    VALUES 
                        ('David', 1, 62000, '2024-01-15'),
                        ('Eve', 3, 59000, '2024-01-15');
                """,
                "explanation": "INSERT multiple rows in a single statement."
            }
        ],
        "update": [
            {
                "question": "Update salary for an employee",
                "solution": """
                    UPDATE employees
                    SET salary = 65000
                    WHERE name = 'Alice';
                """,
                "explanation": "Basic UPDATE statement to modify an employee's salary."
            },
            {
                "question": "Give 10% raise to IT department employees",
                "solution": """
                    UPDATE employees
                    SET salary = salary * 1.1
                    WHERE department_id = 1;
                """,
                "explanation": "UPDATE with calculation and WHERE clause."
            }
        ],
        "delete": [
            {
                "question": "Delete an employee by name",
                "solution": """
                    DELETE FROM employees
                    WHERE name = 'Bob';
                """,
                "explanation": "Basic DELETE statement to remove a specific employee."
            },
            {
                "question": "Delete employees with salary below 55000",
                "solution": """
                    DELETE FROM employees
                    WHERE salary < 55000;
                """,
                "explanation": "DELETE with condition based on salary."
            }
        ],
        "select": [
            {
                "question": "Select employees with their department names",
                "solution": """
                    SELECT e.name, d.name as department
                    FROM employees e
                    JOIN departments d ON e.department_id = d.id;
                """,
                "explanation": "Basic SELECT with JOIN to show employee and department information."
            },
            {
                "question": "Select department-wise average salary",
                "solution": """
                    SELECT d.name, AVG(e.salary) as avg_salary
                    FROM departments d
                    LEFT JOIN employees e ON d.id = e.department_id
                    GROUP BY d.name;
                """,
                "explanation": "SELECT with aggregation and GROUP BY."
            }
        ]
    }

    operation_type = st.selectbox("Select DML Operation:", 
                                list(questions.keys()), 
                                format_func=lambda x: x.upper())
    
    question_index = st.selectbox("Select Question:", 
                                range(1, len(questions[operation_type]) + 1), 
                                format_func=lambda x: f"Question {x}")
    
    selected_question = questions[operation_type][question_index - 1]

    st.subheader("Question:")
    st.write(selected_question["question"])
    
    user_query = st.text_area("Enter your SQL query:")
    
    if st.button("Submit"):
        try:
            cursor.execute(user_query)
            conn.commit()
            
            if operation_type == "select":
                result = cursor.fetchall()
                if result:
                    st.success("Query executed successfully!")
                    st.write("Result:")
                    df = pd.DataFrame(result)
                    st.dataframe(df)
                else:
                    st.warning("Query returned no results.")
            else:
                st.success("Query executed successfully!")
                st.write("Updated Tables:")
                # Show updated data
                cursor.execute("SELECT * FROM employees")
                st.write("Employees Table:")
                df = pd.DataFrame(cursor.fetchall(), 
                                columns=['id', 'name', 'department_id', 'salary', 'hire_date'])
                st.dataframe(df)
                
        except Exception as e:
            st.error(f"Error executing query: {str(e)}")
    
    if st.button("Show Solution", key="show_solution"):
        st.code(selected_question["solution"], language="sql")
        st.write("Explanation:")
        st.write(selected_question["explanation"])

def main():
    st.title("SQL DML Practice App")
    conn = sqlite3.connect(':memory:', check_same_thread=False)
    cursor = conn.cursor()

    try:
        dml_questions(conn, cursor)
    except sqlite3.Error as e:
        st.error(f"An error occurred: {e}")

    conn.close()

if __name__ == "__main__":
    main()
