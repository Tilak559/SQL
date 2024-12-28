import streamlit as st
import sqlite3
import pandas as pd

def window_questions(conn, cursor):
    st.header("SQL Window Functions Practice")
    
    # Drop existing tables
    cursor.execute("DROP TABLE IF EXISTS sales")
    cursor.execute("DROP TABLE IF EXISTS employees")
    
    # Create tables
    cursor.execute("""
        CREATE TABLE employees (
            id INTEGER PRIMARY KEY,
            name TEXT,
            department TEXT,
            salary DECIMAL(10,2),
            hire_date DATE
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
        [(1, 'Alice', 'Sales', 60000, '2023-01-01'),
         (2, 'Bob', 'Sales', 55000, '2023-02-01'),
         (3, 'Charlie', 'Marketing', 65000, '2023-01-15'),
         (4, 'David', 'Marketing', 58000, '2023-03-01'),
         (5, 'Eve', 'IT', 70000, '2023-02-15')])
    
    cursor.executemany("INSERT INTO sales VALUES (?, ?, ?, ?)",
        [(1, 1, 1000, '2024-01-01'),
         (2, 1, 1500, '2024-01-02'),
         (3, 2, 800, '2024-01-01'),
         (4, 2, 1200, '2024-01-02'),
         (5, 3, 2000, '2024-01-01')])
    
    conn.commit()

    # Display tables at the top
    st.subheader("Available Tables:")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Employees Table**")
        cursor.execute("SELECT * FROM employees")
        data = cursor.fetchall()
        df = pd.DataFrame(data, columns=['id', 'name', 'department', 'salary', 'hire_date'])
        st.dataframe(df)
    
    with col2:
        st.write("**Sales Table**")
        cursor.execute("SELECT * FROM sales")
        data = cursor.fetchall()
        df = pd.DataFrame(data, columns=['id', 'employee_id', 'amount', 'sale_date'])
        st.dataframe(df)
    
    st.divider()

    questions = {
        "aggregate_functions": [
            {
                "question": "Calculate department-wise average salary using AVG()",
                "solution": """
                    SELECT department, name, salary,
                           AVG(salary) OVER (PARTITION BY department) as avg_dept_salary
                    FROM employees;
                """
            },
            {
                "question": "Find maximum salary in each department using MAX()",
                "solution": """
                    SELECT department, name, salary,
                           MAX(salary) OVER (PARTITION BY department) as max_dept_salary
                    FROM employees;
                """
            },
            {
                "question": "Calculate minimum salary in each department using MIN()",
                "solution": """
                    SELECT department, name, salary,
                           MIN(salary) OVER (PARTITION BY department) as min_dept_salary
                    FROM employees;
                """
            },
            {
                "question": "Calculate running total of sales using SUM()",
                "solution": """
                    SELECT employee_id, sale_date, amount,
                           SUM(amount) OVER (PARTITION BY employee_id ORDER BY sale_date) as running_total
                    FROM sales;
                """
            },
            {
                "question": "Count employees in each department using COUNT()",
                "solution": """
                    SELECT department, name,
                           COUNT(*) OVER (PARTITION BY department) as dept_emp_count
                    FROM employees;
                """
            }
        ],
        "ranking_functions": [
            {
                "question": "Assign row numbers to employees by salary using ROW_NUMBER()",
                "solution": """
                    SELECT name, salary,
                           ROW_NUMBER() OVER (ORDER BY salary DESC) as salary_rank
                    FROM employees;
                """
            },
            {
                "question": "Rank employees by salary using RANK()",
                "solution": """
                    SELECT name, salary,
                           RANK() OVER (ORDER BY salary DESC) as salary_rank
                    FROM employees;
                """
            },
            {
                "question": "Rank employees without gaps using DENSE_RANK()",
                "solution": """
                    SELECT name, salary,
                           DENSE_RANK() OVER (ORDER BY salary DESC) as dense_salary_rank
                    FROM employees;
                """
            },
            {
                "question": "Calculate percentage rank using PERCENT_RANK()",
                "solution": """
                    SELECT name, salary,
                           PERCENT_RANK() OVER (ORDER BY salary) as salary_percentile
                    FROM employees;
                """
            },
            {
                "question": "Divide employees into quartiles using NTILE()",
                "solution": """
                    SELECT name, salary,
                           NTILE(4) OVER (ORDER BY salary) as salary_quartile
                    FROM employees;
                """
            }
        ],
        "value_functions": [
            {
                "question": "Get previous employee's salary using LAG()",
                "solution": """
                    SELECT name, salary,
                           LAG(salary) OVER (ORDER BY salary) as prev_salary
                    FROM employees;
                """
            },
            {
                "question": "Get next employee's salary using LEAD()",
                "solution": """
                    SELECT name, salary,
                           LEAD(salary) OVER (ORDER BY salary) as next_salary
                    FROM employees;
                """
            },
            {
                "question": "Get first salary in each department using FIRST_VALUE()",
                "solution": """
                    SELECT department, name, salary,
                           FIRST_VALUE(salary) OVER (PARTITION BY department ORDER BY salary) as lowest_salary
                    FROM employees;
                """
            },
            {
                "question": "Get last salary in each department using LAST_VALUE()",
                "solution": """
                    SELECT department, name, salary,
                           LAST_VALUE(salary) OVER (
                               PARTITION BY department 
                               ORDER BY salary 
                               RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
                           ) as highest_salary
                    FROM employees;
                """
            },
            {
                "question": "Get the second highest salary using NTH_VALUE()",
                "solution": """
                    SELECT department, name, salary,
                           NTH_VALUE(salary, 2) OVER (
                               PARTITION BY department 
                               ORDER BY salary DESC
                               RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
                           ) as second_highest_salary
                    FROM employees;
                """
            }
        ]
    }

    function_type = st.selectbox("Select Window Function Type:", 
                               list(questions.keys()), 
                               format_func=lambda x: x.replace('_', ' ').title())
    
    question_index = st.selectbox("Select Question:", 
                                range(1, len(questions[function_type]) + 1), 
                                format_func=lambda x: f"Question {x}")
    
    selected_question = questions[function_type][question_index - 1]

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

def main():
    st.title("SQL Window Functions Practice App")
    conn = sqlite3.connect(':memory:', check_same_thread=False)
    cursor = conn.cursor()

    try:
        window_questions(conn, cursor)
    except sqlite3.Error as e:
        st.error(f"An error occurred: {e}")
        print(f"SQLite error: {e}")

    conn.close()

if __name__ == "__main__":
    main()
