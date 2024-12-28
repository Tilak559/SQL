import streamlit as st
import sqlite3
import pandas as pd

def cte_questions(conn, cursor):
    st.header("SQL CTE Practice")
    
    # Drop existing tables
    cursor.execute("DROP TABLE IF EXISTS sales")
    cursor.execute("DROP TABLE IF EXISTS employees")
    cursor.execute("DROP TABLE IF EXISTS departments")
    
    # Create tables
    cursor.execute("""
        CREATE TABLE employees (
            id INTEGER PRIMARY KEY,
            name TEXT,
            department_id INTEGER,
            manager_id INTEGER,
            salary DECIMAL(10,2),
            hire_date DATE
        )
    """)
    
    cursor.execute("""
        CREATE TABLE departments (
            id INTEGER PRIMARY KEY,
            name TEXT,
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
    cursor.executemany("INSERT INTO employees VALUES (?, ?, ?, ?, ?, ?)",
        [(1, 'John', 1, None, 70000, '2023-01-01'),
         (2, 'Alice', 1, 1, 60000, '2023-02-01'),
         (3, 'Bob', 2, 1, 55000, '2023-01-15'),
         (4, 'Charlie', 2, 3, 50000, '2023-03-01'),
         (5, 'David', 1, 2, 52000, '2023-02-15')])
    
    cursor.executemany("INSERT INTO departments VALUES (?, ?, ?)",
        [(1, 'Sales', 500000),
         (2, 'Marketing', 400000)])
    
    cursor.executemany("INSERT INTO sales VALUES (?, ?, ?, ?)",
        [(1, 2, 5000, '2024-01-01'),
         (2, 2, 4500, '2024-01-02'),
         (3, 3, 3000, '2024-01-01'),
         (4, 3, 3500, '2024-01-02'),
         (5, 4, 2000, '2024-01-01')])
    
    conn.commit()

    # Display tables at the top
    st.subheader("Available Tables:")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**Employees Table**")
        cursor.execute("SELECT * FROM employees")
        data = cursor.fetchall()
        df = pd.DataFrame(data, columns=['id', 'name', 'department_id', 'manager_id', 'salary', 'hire_date'])
        st.dataframe(df)
    
    with col2:
        st.write("**Departments Table**")
        cursor.execute("SELECT * FROM departments")
        data = cursor.fetchall()
        df = pd.DataFrame(data, columns=['id', 'name', 'budget'])
        st.dataframe(df)
    
    with col3:
        st.write("**Sales Table**")
        cursor.execute("SELECT * FROM sales")
        data = cursor.fetchall()
        df = pd.DataFrame(data, columns=['id', 'employee_id', 'amount', 'sale_date'])
        st.dataframe(df)
    
    st.divider()

    questions = {
        "simple_cte": [
            {
                "question": "Calculate average salary using CTE",
                "solution": """
                    WITH avg_sal AS (
                        SELECT AVG(salary) as avg_salary
                        FROM employees
                    )
                    SELECT e.name, e.salary, avg_sal.avg_salary,
                           e.salary - avg_sal.avg_salary as difference
                    FROM employees e, avg_sal
                    WHERE e.salary > avg_sal.avg_salary;
                """,
                "explanation": "Uses a simple CTE to calculate average salary and compare each employee's salary to it."
            },
            {
                "question": "Find top sales performers using CTE",
                "solution": """
                    WITH sales_total AS (
                        SELECT employee_id, SUM(amount) as total_sales
                        FROM sales
                        GROUP BY employee_id
                    )
                    SELECT e.name, st.total_sales
                    FROM sales_total st
                    JOIN employees e ON e.id = st.employee_id
                    ORDER BY st.total_sales DESC;
                """,
                "explanation": "Uses CTE to calculate total sales per employee and rank them."
            }
        ],
        "recursive_cte": [
            {
                "question": "Create employee hierarchy using recursive CTE",
                "solution": """
                    WITH RECURSIVE emp_hierarchy AS (
                        SELECT id, name, manager_id, 0 as level
                        FROM employees
                        WHERE manager_id IS NULL
                        UNION ALL
                        SELECT e.id, e.name, e.manager_id, eh.level + 1
                        FROM employees e
                        JOIN emp_hierarchy eh ON e.manager_id = eh.id
                    )
                    SELECT * FROM emp_hierarchy ORDER BY level, id;
                """,
                "explanation": "Uses recursive CTE to build organizational hierarchy showing reporting relationships."
            },
            {
                "question": "Generate date series between sales dates",
                "solution": """
                    WITH RECURSIVE date_series AS (
                        SELECT MIN(sale_date) as date
                        FROM sales
                        UNION ALL
                        SELECT date(date, '+1 day')
                        FROM date_series
                        WHERE date < (SELECT MAX(sale_date) FROM sales)
                    )
                    SELECT date FROM date_series;
                """,
                "explanation": "Uses recursive CTE to generate series of dates between first and last sale."
            }
        ],
        "multiple_cte": [
            {
                "question": "Calculate department statistics using multiple CTEs",
                "solution": """
                    WITH dept_totals AS (
                        SELECT department_id,
                               COUNT(*) as emp_count,
                               AVG(salary) as avg_salary
                        FROM employees
                        GROUP BY department_id
                    ),
                    dept_sales AS (
                        SELECT e.department_id,
                               SUM(s.amount) as total_sales
                        FROM sales s
                        JOIN employees e ON s.employee_id = e.id
                        GROUP BY e.department_id
                    )
                    SELECT d.name, dt.emp_count, dt.avg_salary, 
                           COALESCE(ds.total_sales, 0) as total_sales
                    FROM departments d
                    LEFT JOIN dept_totals dt ON d.id = dt.department_id
                    LEFT JOIN dept_sales ds ON d.id = ds.department_id;
                """,
                "explanation": "Uses multiple CTEs to calculate various department metrics including employee counts and sales totals."
            }
        ]
    }

    cte_type = st.selectbox("Select CTE Type:", 
                           list(questions.keys()), 
                           format_func=lambda x: x.replace('_', ' ').title())
    
    question_index = st.selectbox("Select Question:", 
                                range(1, len(questions[cte_type]) + 1), 
                                format_func=lambda x: f"Question {x}")
    
    selected_question = questions[cte_type][question_index - 1]

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
    st.title("SQL CTE Practice App")
    conn = sqlite3.connect(':memory:', check_same_thread=False)
    cursor = conn.cursor()

    try:
        cte_questions(conn, cursor)
    except sqlite3.Error as e:
        st.error(f"An error occurred: {e}")
        print(f"SQLite error: {e}")

    conn.close()

if __name__ == "__main__":
    main()
