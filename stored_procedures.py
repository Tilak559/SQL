import streamlit as st
import sqlite3
import pandas as pd

def stored_procedure_app(conn, cursor):
    st.header("SQL Stored Procedures Practice")
    
    # Create tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY,
            name TEXT,
            department_id INTEGER,
            salary DECIMAL(10,2)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY,
            name TEXT,
            budget DECIMAL(10,2)
        )
    """)
    
    # Insert sample data
    cursor.executemany("INSERT OR IGNORE INTO employees VALUES (?, ?, ?, ?)",
        [(1, 'John', 1, 60000),
         (2, 'Alice', 1, 55000),
         (3, 'Bob', 2, 65000)])
    
    cursor.executemany("INSERT OR IGNORE INTO departments VALUES (?, ?, ?)",
        [(1, 'IT', 100000),
         (2, 'HR', 80000)])
    
    conn.commit()

    # Display tables
    st.subheader("Available Tables:")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Employees Table**")
        cursor.execute("SELECT * FROM employees")
        df = pd.DataFrame(cursor.fetchall(), columns=['id', 'name', 'department_id', 'salary'])
        st.dataframe(df)
    
    with col2:
        st.write("**Departments Table**")
        cursor.execute("SELECT * FROM departments")
        df = pd.DataFrame(cursor.fetchall(), columns=['id', 'name', 'budget'])
        st.dataframe(df)

    # Stored Procedure Functions
    def get_employee_by_id(emp_id):
        cursor.execute("""
            SELECT e.*, d.name as department_name
            FROM employees e
            LEFT JOIN departments d ON e.department_id = d.id
            WHERE e.id = ?
        """, (emp_id,))
        return cursor.fetchall()

    def update_employee_salary(emp_id, new_salary):
        cursor.execute("""
            UPDATE employees 
            SET salary = ?
            WHERE id = ?
        """, (new_salary, emp_id))
        conn.commit()

    def get_department_employees(dept_id):
        cursor.execute("""
            SELECT e.name, e.salary
            FROM employees e
            WHERE e.department_id = ?
        """, (dept_id,))
        return cursor.fetchall()

    def calculate_department_stats(dept_id):
        cursor.execute("""
            SELECT 
                d.name,
                COUNT(e.id) as employee_count,
                AVG(e.salary) as avg_salary,
                MAX(e.salary) as max_salary,
                MIN(e.salary) as min_salary
            FROM departments d
            LEFT JOIN employees e ON d.id = e.department_id
            WHERE d.id = ?
            GROUP BY d.id
        """, (dept_id,))
        return cursor.fetchall()

    # Procedure Selection and Execution
    procedure_options = {
        "Get Employee Details": get_employee_by_id,
        "Update Employee Salary": update_employee_salary,
        "Get Department Employees": get_department_employees,
        "Calculate Department Statistics": calculate_department_stats
    }

    selected_procedure = st.selectbox("Select Procedure:", list(procedure_options.keys()))

    if selected_procedure == "Get Employee Details":
        emp_id = st.number_input("Enter Employee ID:", min_value=1)
        if st.button("Execute"):
            result = procedure_options[selected_procedure](emp_id)
            st.write("Result:")
            st.dataframe(pd.DataFrame(result))

    elif selected_procedure == "Update Employee Salary":
        emp_id = st.number_input("Enter Employee ID:", min_value=1)
        new_salary = st.number_input("Enter New Salary:", min_value=0.0)
        if st.button("Execute"):
            procedure_options[selected_procedure](emp_id, new_salary)
            st.success("Salary updated successfully!")

    elif selected_procedure == "Get Department Employees":
        dept_id = st.number_input("Enter Department ID:", min_value=1)
        if st.button("Execute"):
            result = procedure_options[selected_procedure](dept_id)
            st.write("Result:")
            st.dataframe(pd.DataFrame(result))

    elif selected_procedure == "Calculate Department Statistics":
        dept_id = st.number_input("Enter Department ID:", min_value=1)
        if st.button("Execute"):
            result = procedure_options[selected_procedure](dept_id)
            st.write("Result:")
            st.dataframe(pd.DataFrame(result))

def main():
    st.title("SQL Stored Procedures Practice App")
    conn = sqlite3.connect(':memory:', check_same_thread=False)
    cursor = conn.cursor()

    try:
        stored_procedure_app(conn, cursor)
    except sqlite3.Error as e:
        st.error(f"An error occurred: {e}")

    conn.close()

if __name__ == "__main__":
    main()
