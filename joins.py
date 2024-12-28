import streamlit as st
import sqlite3
import pandas as pd

def joins_questions(conn, cursor):
    st.header("SQL JOIN Practice")
    
    # Drop existing tables
    cursor.execute("DROP TABLE IF EXISTS employees")
    cursor.execute("DROP TABLE IF EXISTS departments")
    cursor.execute("DROP TABLE IF EXISTS projects")
    
    # Create tables with correct structure
    cursor.execute("""
        CREATE TABLE employees (
            id INTEGER PRIMARY KEY,
            name TEXT,
            department_id INTEGER
        )
    """)
    cursor.execute("""
        CREATE TABLE departments (
            id INTEGER PRIMARY KEY,
            name TEXT,
            location TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE projects (
            id INTEGER PRIMARY KEY,
            name TEXT,
            department_id INTEGER
        )
    """)
    
    # Insert sample data
    cursor.executemany("INSERT INTO employees (id, name, department_id) VALUES (?, ?, ?)",
                       [(1, 'Alice', 1), (2, 'Bob', 2), (3, 'Charlie', 1), (4, 'David', 3), (5, 'Eve', None)])
    cursor.executemany("INSERT INTO departments (id, name, location) VALUES (?, ?, ?)",
                       [(1, 'IT', 'New York'), (2, 'HR', 'London'), (3, 'Finance', 'Tokyo'), (4, 'Marketing', 'Paris')])
    cursor.executemany("INSERT INTO projects (id, name, department_id) VALUES (?, ?, ?)",
                       [(1, 'Website Redesign', 1), (2, 'Employee Training', 2), (3, 'Budget Analysis', 3), (4, 'New Product Launch', 4)])
    conn.commit()

    # Display tables at the top
    st.subheader("Available Tables:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**Employees Table**")
        cursor.execute("SELECT * FROM employees")
        data = cursor.fetchall()
        df = pd.DataFrame(data, columns=['id', 'name', 'department_id'])
        st.dataframe(df)
    
    with col2:
        st.write("**Departments Table**")
        cursor.execute("SELECT * FROM departments")
        data = cursor.fetchall()
        df = pd.DataFrame(data, columns=['id', 'name', 'location'])
        st.dataframe(df)
    
    with col3:
        st.write("**Projects Table**")
        cursor.execute("SELECT * FROM projects")
        data = cursor.fetchall()
        df = pd.DataFrame(data, columns=['id', 'name', 'department_id'])
        st.dataframe(df)
    
    st.divider()

    questions = {
        "inner_join": [
            {
                "question": "List all employees with their department names",
                "solution": """
                    SELECT e.name AS employee_name, d.name AS department_name
                    FROM employees e
                    INNER JOIN departments d ON e.department_id = d.id
                """,
                "explanation": "This query uses an INNER JOIN to match employees with their departments, showing only employees who have a department assigned."
            },
            {
                "question": "Show all projects with their associated department names",
                "solution": """
                    SELECT p.name AS project_name, d.name AS department_name
                    FROM projects p
                    INNER JOIN departments d ON p.department_id = d.id
                """,
                "explanation": "This INNER JOIN connects projects to their respective departments, displaying only projects that have a department assigned."
            },
            {
                "question": "List employees, their departments, and assigned projects",
                "solution": """
                    SELECT e.name AS employee_name, d.name AS department_name, p.name AS project_name
                    FROM employees e
                    INNER JOIN departments d ON e.department_id = d.id
                    INNER JOIN projects p ON d.id = p.department_id
                """,
                "explanation": "This query uses two INNER JOINs to connect employees with their departments and the projects assigned to those departments."
            }
        ],
        "left_join": [
            {
                "question": "List all employees and their department names (if any)",
                "solution": """
                    SELECT e.name AS employee_name, d.name AS department_name
                    FROM employees e
                    LEFT JOIN departments d ON e.department_id = d.id
                """,
                "explanation": "This LEFT JOIN returns all employees, including those without a department (which will show as NULL for department_name)."
            },
            {
                "question": "Show all departments and the number of employees in each",
                "solution": """
                    SELECT d.name AS department_name, COUNT(e.id) AS employee_count
                    FROM departments d
                    LEFT JOIN employees e ON d.id = e.department_id
                    GROUP BY d.id, d.name
                """,
                "explanation": "This LEFT JOIN ensures all departments are listed, even those without employees. The COUNT function gives the number of employees per department."
            },
            {
                "question": "List all projects and their department names (if any)",
                "solution": """
                    SELECT p.name AS project_name, d.name AS department_name
                    FROM projects p
                    LEFT JOIN departments d ON p.department_id = d.id
                """,
                "explanation": "This LEFT JOIN shows all projects, including those not assigned to any department (which will have NULL for department_name)."
            }
        ],
        "right_join": [
            {
                "question": "List all departments and employees assigned to them (if any)",
                "solution": """
                    SELECT d.name AS department_name, e.name AS employee_name
                    FROM employees e
                    RIGHT JOIN departments d ON e.department_id = d.id
                """,
                "explanation": "This RIGHT JOIN ensures all departments are listed, even those without employees. Note: SQLite doesn't support RIGHT JOIN, so this is simulated with a LEFT JOIN by switching the table order."
            },
            {
                "question": "Show all department locations and the projects running there (if any)",
                "solution": """
                    SELECT d.location, p.name AS project_name
                    FROM projects p
                    RIGHT JOIN departments d ON p.department_id = d.id
                """,
                "explanation": "This RIGHT JOIN lists all department locations, including those without any projects. (Simulated in SQLite)"
            },
            {
                "question": "List all departments and the number of projects in each",
                "solution": """
                    SELECT d.name AS department_name, COUNT(p.id) AS project_count
                    FROM projects p
                    RIGHT JOIN departments d ON p.department_id = d.id
                    GROUP BY d.id, d.name
                """,
                "explanation": "This RIGHT JOIN counts projects for each department, including departments with zero projects. (Simulated in SQLite)"
            }
        ],
        "full_outer_join": [
            {
                "question": "List all employees and departments, showing all possible combinations",
                "solution": """
                    SELECT e.name AS employee_name, d.name AS department_name
                    FROM employees e
                    LEFT JOIN departments d ON e.department_id = d.id
                    UNION ALL
                    SELECT e.name AS employee_name, d.name AS department_name
                    FROM departments d
                    LEFT JOIN employees e ON d.id = e.department_id
                    WHERE e.id IS NULL
                """,
                "explanation": "This simulates a FULL OUTER JOIN in SQLite by combining a LEFT JOIN with a UNION ALL to include unmatched rows from both tables."
            },
            {
                "question": "Show all projects and departments, including unmatched records",
                "solution": """
                    SELECT p.name AS project_name, d.name AS department_name
                    FROM projects p
                    LEFT JOIN departments d ON p.department_id = d.id
                    UNION ALL
                    SELECT p.name AS project_name, d.name AS department_name
                    FROM departments d
                    LEFT JOIN projects p ON d.id = p.department_id
                    WHERE p.id IS NULL
                """,
                "explanation": "This query simulates a FULL OUTER JOIN between projects and departments, showing all projects and all departments, even if there's no match."
            },
            {
                "question": "List all employees, departments, and projects, showing all possible combinations",
                "solution": """
                    SELECT e.name AS employee_name, d.name AS department_name, p.name AS project_name
                    FROM employees e
                    LEFT JOIN departments d ON e.department_id = d.id
                    LEFT JOIN projects p ON d.id = p.department_id
                    UNION ALL
                    SELECT e.name AS employee_name, d.name AS department_name, p.name AS project_name
                    FROM departments d
                    LEFT JOIN employees e ON d.id = e.department_id
                    LEFT JOIN projects p ON d.id = p.department_id
                    WHERE e.id IS NULL
                    UNION ALL
                    SELECT e.name AS employee_name, d.name AS department_name, p.name AS project_name
                    FROM projects p
                    LEFT JOIN departments d ON p.department_id = d.id
                    LEFT JOIN employees e ON d.id = e.department_id
                    WHERE d.id IS NULL
                """,
                "explanation": "This complex query simulates a FULL OUTER JOIN across three tables, showing all possible combinations of employees, departments, and projects."
            }
        ],
        "cross_join": [
            {
                "question": "Generate all possible employee-department combinations",
                "solution": """
                    SELECT e.name AS employee_name, d.name AS department_name
                    FROM employees e
                    CROSS JOIN departments d
                """,
                "explanation": "This CROSS JOIN creates a Cartesian product of all employees with all departments, useful for generating all possible combinations."
            },
            {
                "question": "List all possible project-location combinations",
                "solution": """
                    SELECT p.name AS project_name, d.location
                    FROM projects p
                    CROSS JOIN departments d
                """,
                "explanation": "This CROSS JOIN shows every project combined with every department location, which could be useful for planning or hypothetical scenarios."
            },
            {
                "question": "Generate a matrix of all employees and all projects",
                "solution": """
                    SELECT e.name AS employee_name, p.name AS project_name
                    FROM employees e
                    CROSS JOIN projects p
                """,
                "explanation": "This CROSS JOIN creates a matrix of all employees with all projects, which could be used for assignment possibilities or workload distribution scenarios."
            }
        ]
    }

    join_type = st.selectbox("Select JOIN type:", list(questions.keys()), format_func=lambda x: x.replace('_', ' ').title())
    question_index = st.selectbox("Select question:", range(1, 4), format_func=lambda x: f"Question {x}")
    
    selected_question = questions[join_type][question_index - 1]

    st.subheader("Question:")
    st.write(selected_question["question"])
    
    user_query = st.text_area("Enter your SQL query:")
    
    if st.button("Submit"):
        try:
            cursor.execute(user_query)
            result = cursor.fetchall()
            
            if result:
                st.success("Query executed successfully!")
                st.write("Result:")
                df = pd.DataFrame(result)
                st.dataframe(df)
            else:
                st.warning("Query executed but returned no results.")
                
        except Exception as e:
            st.error(f"Error executing query: {str(e)}")
    
    if st.button("Show Solution", key="show_solution"):
        st.code(selected_question["solution"], language="sql")
        st.write("Explanation:")
        st.write(selected_question["explanation"])

def main():
    st.title("SQL JOIN Practice App")

    conn = sqlite3.connect(':memory:', check_same_thread=False)
    cursor = conn.cursor()

    try:
        joins_questions(conn, cursor)
    except sqlite3.Error as e:
        st.error(f"An error occurred: {e}")
        print(f"SQLite error: {e}")

    conn.close()

if __name__ == "__main__":
    main()
