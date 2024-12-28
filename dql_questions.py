import streamlit as st
import sqlite3
import pandas as pd

def dql_questions(conn, cursor):
    st.header("SQL DQL Practice")
    
    # Drop existing tables
    cursor.execute("DROP TABLE IF EXISTS employees")
    cursor.execute("DROP TABLE IF EXISTS departments")
    cursor.execute("DROP TABLE IF EXISTS sales")
    
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
    
    cursor.execute("""
        CREATE TABLE sales (
            id INTEGER PRIMARY KEY,
            employee_id INTEGER,
            amount DECIMAL(10,2),
            sale_date DATE
        )
    """)
    
    # Insert sample data
    cursor.executemany("INSERT INTO employees VALUES (?, ?, ?, ?, ?)",
        [(1, 'John', 1, 60000, '2023-01-01'),
         (2, 'Alice', 1, 55000, '2023-02-01'),
         (3, 'Bob', 2, 65000, '2023-01-15'),
         (4, 'Charlie', 2, 50000, '2023-03-01'),
         (5, 'David', 1, 58000, '2023-04-01')])
    
    cursor.executemany("INSERT INTO departments VALUES (?, ?, ?, ?)",
        [(1, 'Sales', 'New York', 500000),
         (2, 'Marketing', 'London', 400000)])
    
    cursor.executemany("INSERT INTO sales VALUES (?, ?, ?, ?)",
        [(1, 1, 5000, '2024-01-01'),
         (2, 1, 4500, '2024-01-02'),
         (3, 2, 3000, '2024-01-01'),
         (4, 2, 3500, '2024-01-02'),
         (5, 3, 2000, '2024-01-01')])
    
    conn.commit()

    # Display tables
    st.subheader("Available Tables:")
    col1, col2, col3 = st.columns(3)
    
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
    
    with col3:
        st.write("**Sales Table**")
        cursor.execute("SELECT * FROM sales")
        df = pd.DataFrame(cursor.fetchall(), 
                         columns=['id', 'employee_id', 'amount', 'sale_date'])
        st.dataframe(df)

    st.divider()

    questions = {
        "basic_select": [
            {
                "question": "Select all employees with salary above 55000",
                "solution": """
                    SELECT name, salary 
                    FROM employees 
                    WHERE salary > 55000;
                """,
                "explanation": "Basic SELECT with WHERE clause to filter employees by salary."
            },
            {
                "question": "Select employees hired in first quarter of 2023",
                "solution": """
                    SELECT name, hire_date 
                    FROM employees 
                    WHERE hire_date BETWEEN '2023-01-01' AND '2023-03-31';
                """,
                "explanation": "Using BETWEEN operator to filter dates."
            }
        ],
        "aggregate_functions": [
            {
                "question": "Calculate average salary by department",
                "solution": """
                    SELECT d.name, AVG(e.salary) as avg_salary
                    FROM employees e
                    JOIN departments d ON e.department_id = d.id
                    GROUP BY d.name;
                """,
                "explanation": "Using aggregate function AVG with GROUP BY."
            },
            {
                "question": "Count number of sales per employee",
                "solution": """
                    SELECT e.name, COUNT(s.id) as sale_count
                    FROM employees e
                    LEFT JOIN sales s ON e.id = s.employee_id
                    GROUP BY e.name;
                """,
                "explanation": "Using COUNT with LEFT JOIN to include employees with no sales."
            }
        ],
        "complex_queries": [
            {
                "question": "Find employees with total sales above average",
                "solution": """
                    WITH emp_sales AS (
                        SELECT e.name, SUM(s.amount) as total_sales
                        FROM employees e
                        LEFT JOIN sales s ON e.id = s.employee_id
                        GROUP BY e.name
                    )
                    SELECT name, total_sales
                    FROM emp_sales
                    WHERE total_sales > (SELECT AVG(total_sales) FROM emp_sales);
                """,
                "explanation": "Using CTE and subquery to compare against average."
            },
            {
                "question": "Rank employees by salary within departments",
                "solution": """
                    SELECT 
                        e.name,
                        d.name as department,
                        e.salary,
                        RANK() OVER (PARTITION BY e.department_id ORDER BY e.salary DESC) as salary_rank
                    FROM employees e
                    JOIN departments d ON e.department_id = d.id;
                """,
                "explanation": "Using window function RANK to rank employees by salary."
            }
        ]
    }

    query_type = st.selectbox("Select Query Type:", 
                            list(questions.keys()), 
                            format_func=lambda x: x.replace('_', ' ').title())
    
    question_index = st.selectbox("Select Question:", 
                                range(1, len(questions[query_type]) + 1), 
                                format_func=lambda x: f"Question {x}")
    
    selected_question = questions[query_type][question_index - 1]

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
                st.warning("Query returned no results.")
        except Exception as e:
            st.error(f"Error executing query: {str(e)}")
    
    if st.button("Show Solution", key="show_solution"):
        st.code(selected_question["solution"], language="sql")
        st.write("Explanation:")
        st.write(selected_question["explanation"])

def main():
    st.title("SQL DQL Practice App")
    conn = sqlite3.connect(':memory:', check_same_thread=False)
    cursor = conn.cursor()

    try:
        dql_questions(conn, cursor)
    except sqlite3.Error as e:
        st.error(f"An error occurred: {e}")

    conn.close()

if __name__ == "__main__":
    main()
