import streamlit as st
import sqlite3
import pandas as pd

def trigger_questions(conn, cursor):
    st.header("SQL Triggers Practice")
    
    # Drop existing tables
    cursor.execute("DROP TABLE IF EXISTS employees")
    cursor.execute("DROP TABLE IF EXISTS salary_changes")
    cursor.execute("DROP TABLE IF EXISTS audit_log")
    
    # Create tables
    cursor.execute("""
        CREATE TABLE employees (
            id INTEGER PRIMARY KEY,
            name TEXT,
            department TEXT,
            salary DECIMAL(10,2)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE salary_changes (
            id INTEGER PRIMARY KEY,
            employee_id INTEGER,
            old_salary DECIMAL(10,2),
            new_salary DECIMAL(10,2),
            change_date DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE audit_log (
            id INTEGER PRIMARY KEY,
            table_name TEXT,
            action TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Insert sample data
    cursor.executemany("INSERT INTO employees VALUES (?, ?, ?, ?)",
        [(1, 'John', 'IT', 60000),
         (2, 'Alice', 'HR', 55000),
         (3, 'Bob', 'IT', 65000)])
    
    conn.commit()

    # Display tables
    st.subheader("Available Tables:")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**Employees Table**")
        cursor.execute("SELECT * FROM employees")
        data = cursor.fetchall()
        df = pd.DataFrame(data, columns=['id', 'name', 'department', 'salary'])
        st.dataframe(df)
    
    with col2:
        st.write("**Salary Changes Table**")
        cursor.execute("SELECT * FROM salary_changes")
        data = cursor.fetchall()
        df = pd.DataFrame(data, columns=['id', 'employee_id', 'old_salary', 'new_salary', 'change_date'])
        st.dataframe(df)
    
    with col3:
        st.write("**Audit Log Table**")
        cursor.execute("SELECT * FROM audit_log")
        data = cursor.fetchall()
        df = pd.DataFrame(data, columns=['id', 'table_name', 'action', 'timestamp'])
        st.dataframe(df)

    st.divider()

    questions = {
        "before_triggers": [
            {
                "question": "Create a BEFORE INSERT trigger to validate salary",
                "solution": """
                    CREATE TRIGGER validate_salary
                    BEFORE INSERT ON employees
                    BEGIN
                        SELECT CASE
                            WHEN NEW.salary < 0 THEN
                                RAISE(ABORT, 'Salary cannot be negative')
                        END;
                    END;
                """,
                "explanation": "This trigger ensures that no employee can be inserted with a negative salary."
            },
            {
                "question": "Create a BEFORE UPDATE trigger to prevent salary decrease",
                "solution": """
                    CREATE TRIGGER prevent_salary_decrease
                    BEFORE UPDATE ON employees
                    WHEN NEW.salary < OLD.salary
                    BEGIN
                        SELECT RAISE(ABORT, 'Salary cannot be decreased');
                    END;
                """,
                "explanation": "This trigger prevents updating an employee's salary to a lower value."
            }
        ],
        "after_triggers": [
            {
                "question": "Create an AFTER UPDATE trigger to log salary changes",
                "solution": """
                    CREATE TRIGGER log_salary_change
                    AFTER UPDATE OF salary ON employees
                    BEGIN
                        INSERT INTO salary_changes (employee_id, old_salary, new_salary)
                        VALUES (OLD.id, OLD.salary, NEW.salary);
                    END;
                """,
                "explanation": "This trigger logs all salary changes in the salary_changes table."
            },
            {
                "question": "Create an AFTER DELETE trigger to audit employee deletions",
                "solution": """
                    CREATE TRIGGER audit_employee_deletion
                    AFTER DELETE ON employees
                    BEGIN
                        INSERT INTO audit_log (table_name, action)
                        VALUES ('employees', 'DELETE');
                    END;
                """,
                "explanation": "This trigger records all employee deletions in the audit_log table."
            }
        ],
        "compound_triggers": [
            {
                "question": "Create triggers for complete employee audit trail",
                "solution": """
                    -- Trigger for INSERT
                    CREATE TRIGGER audit_employee_insert
                    AFTER INSERT ON employees
                    BEGIN
                        INSERT INTO audit_log (table_name, action)
                        VALUES ('employees', 'INSERT');
                    END;
                    
                    -- Trigger for UPDATE
                    CREATE TRIGGER audit_employee_update
                    AFTER UPDATE ON employees
                    BEGIN
                        INSERT INTO audit_log (table_name, action)
                        VALUES ('employees', 'UPDATE');
                    END;
                    
                    -- Trigger for DELETE
                    CREATE TRIGGER audit_employee_delete
                    AFTER DELETE ON employees
                    BEGIN
                        INSERT INTO audit_log (table_name, action)
                        VALUES ('employees', 'DELETE');
                    END;
                """,
                "explanation": "These triggers create a complete audit trail by logging all INSERT, UPDATE, and DELETE operations."
            }
        ]
    }

    trigger_type = st.selectbox("Select Trigger Type:", 
                              list(questions.keys()), 
                              format_func=lambda x: x.replace('_', ' ').title())
    
    question_index = st.selectbox("Select Question:", 
                                range(1, len(questions[trigger_type]) + 1), 
                                format_func=lambda x: f"Question {x}")
    
    selected_question = questions[trigger_type][question_index - 1]

    st.subheader("Question:")
    st.write(selected_question["question"])
    
    user_query = st.text_area("Enter your SQL query:")
    
    if st.button("Submit"):
        try:
            cursor.execute(user_query)
            conn.commit()
            st.success("Trigger created successfully!")
            
            # Test the trigger
            st.write("Testing trigger with sample data...")
            if "salary" in user_query.lower():
                cursor.execute("UPDATE employees SET salary = 70000 WHERE id = 1")
            elif "delete" in user_query.lower():
                cursor.execute("DELETE FROM employees WHERE id = 3")
            conn.commit()
            
            # Show updated tables
            st.write("Updated tables:")
            cursor.execute("SELECT * FROM employees")
            st.dataframe(pd.DataFrame(cursor.fetchall(), 
                        columns=['id', 'name', 'department', 'salary']))
            
        except Exception as e:
            st.error(f"Error creating trigger: {str(e)}")
    
    if st.button("Show Solution", key="show_solution"):
        st.code(selected_question["solution"], language="sql")
        st.write("Explanation:")
        st.write(selected_question["explanation"])

def main():
    st.title("SQL Triggers Practice App")
    conn = sqlite3.connect(':memory:', check_same_thread=False)
    cursor = conn.cursor()

    try:
        trigger_questions(conn, cursor)
    except sqlite3.Error as e:
        st.error(f"An error occurred: {e}")
        print(f"SQLite error: {e}")

    conn.close()

if __name__ == "__main__":
    main()
