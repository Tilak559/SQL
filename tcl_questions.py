import streamlit as st
import sqlite3
import pandas as pd

def tcl_questions(conn, cursor):
    st.header("SQL TCL Practice")
    
    # Drop existing tables
    cursor.execute("DROP TABLE IF EXISTS accounts")
    cursor.execute("DROP TABLE IF EXISTS transactions")
    
    # Create tables
    cursor.execute("""
        CREATE TABLE accounts (
            id INTEGER PRIMARY KEY,
            name TEXT,
            balance DECIMAL(10,2)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE transactions (
            id INTEGER PRIMARY KEY,
            account_id INTEGER,
            type TEXT,
            amount DECIMAL(10,2),
            transaction_date DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Insert sample data
    cursor.executemany("INSERT INTO accounts VALUES (?, ?, ?)",
        [(1, 'John', 1000.00),
         (2, 'Alice', 2000.00),
         (3, 'Bob', 1500.00)])
    
    conn.commit()

    # Display tables
    st.subheader("Available Tables:")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Accounts Table**")
        cursor.execute("SELECT * FROM accounts")
        df = pd.DataFrame(cursor.fetchall(), columns=['id', 'name', 'balance'])
        st.dataframe(df)
    
    with col2:
        st.write("**Transactions Table**")
        cursor.execute("SELECT * FROM transactions")
        df = pd.DataFrame(cursor.fetchall(), 
                         columns=['id', 'account_id', 'type', 'amount', 'transaction_date'])
        st.dataframe(df)

    st.divider()

    questions = {
        "begin_transaction": [
            {
                "question": "Start a new transaction",
                "solution": """
                    BEGIN TRANSACTION;
                """,
                "explanation": "Starts a new transaction block."
            }
        ],
        "commit": [
            {
                "question": "Transfer money between accounts and commit the transaction",
                "solution": """
                    BEGIN TRANSACTION;
                    UPDATE accounts SET balance = balance - 500 WHERE id = 1;
                    UPDATE accounts SET balance = balance + 500 WHERE id = 2;
                    INSERT INTO transactions (account_id, type, amount) 
                    VALUES (1, 'TRANSFER_OUT', 500), (2, 'TRANSFER_IN', 500);
                    COMMIT;
                """,
                "explanation": "Commits a transaction after successful money transfer between accounts."
            }
        ],
        "rollback": [
            {
                "question": "Rollback a failed transaction",
                "solution": """
                    BEGIN TRANSACTION;
                    UPDATE accounts SET balance = balance - 5000 WHERE id = 1;
                    -- Check if balance would go negative
                    SELECT CASE 
                        WHEN (SELECT balance FROM accounts WHERE id = 1) < 0 
                        THEN RAISE(ROLLBACK, 'Insufficient funds')
                    END;
                    ROLLBACK;
                """,
                "explanation": "Rolls back a transaction if the account balance would go negative."
            }
        ],
        "savepoint": [
            {
                "question": "Use savepoint in a transaction",
                "solution": """
                    BEGIN TRANSACTION;
                    SAVEPOINT before_transfer;
                    UPDATE accounts SET balance = balance - 100 WHERE id = 1;
                    -- If something goes wrong
                    ROLLBACK TO SAVEPOINT before_transfer;
                    COMMIT;
                """,
                "explanation": "Creates a savepoint to roll back to if needed within a transaction."
            }
        ]
    }

    tcl_type = st.selectbox("Select TCL Operation:", 
                           list(questions.keys()), 
                           format_func=lambda x: x.replace('_', ' ').title())
    
    question_index = st.selectbox("Select Question:", 
                                range(1, len(questions[tcl_type]) + 1), 
                                format_func=lambda x: f"Question {x}")
    
    selected_question = questions[tcl_type][question_index - 1]

    st.subheader("Question:")
    st.write(selected_question["question"])
    
    user_query = st.text_area("Enter your SQL query:")
    
    if st.button("Submit"):
        try:
            # Split multiple statements
            statements = user_query.split(';')
            for statement in statements:
                if statement.strip():
                    cursor.execute(statement)
            conn.commit()
            
            st.success("Transaction executed successfully!")
            st.write("Updated Tables:")
            
            # Show updated data
            cursor.execute("SELECT * FROM accounts")
            st.write("Accounts Table:")
            df = pd.DataFrame(cursor.fetchall(), columns=['id', 'name', 'balance'])
            st.dataframe(df)
            
            cursor.execute("SELECT * FROM transactions")
            st.write("Transactions Table:")
            df = pd.DataFrame(cursor.fetchall(), 
                            columns=['id', 'account_id', 'type', 'amount', 'transaction_date'])
            st.dataframe(df)
            
        except Exception as e:
            st.error(f"Error executing transaction: {str(e)}")
            cursor.execute("ROLLBACK")
    
    if st.button("Show Solution", key="show_solution"):
        st.code(selected_question["solution"], language="sql")
        st.write("Explanation:")
        st.write(selected_question["explanation"])

def main():
    st.title("SQL TCL Practice App")
    conn = sqlite3.connect(':memory:', check_same_thread=False)
    cursor = conn.cursor()

    try:
        tcl_questions(conn, cursor)
    except sqlite3.Error as e:
        st.error(f"An error occurred: {e}")

    conn.close()

if __name__ == "__main__":
    main()
