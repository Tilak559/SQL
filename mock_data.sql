-- Create the questions table
CREATE TABLE questions (
    id INTEGER PRIMARY KEY,
    topic TEXT NOT NULL,
    question_text TEXT NOT NULL,
    expected_output_query TEXT NOT NULL,
    explanation TEXT
);

-- Create the employees table
CREATE TABLE employees (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    age INTEGER NOT NULL,
    department TEXT NOT NULL,
    salary INTEGER NOT NULL
);

-- Insert sample data into employees table
INSERT INTO employees (id, name, age, department, salary) VALUES
(1, 'Alice', 30, 'HR', 5000),
(2, 'Bob', 25, 'Engineering', 7000),
(3, 'Charlie', 35, 'Finance', 8000),
(4, 'David', 40, 'Engineering', 9000);

-- Insert questions into the questions table
INSERT INTO questions (topic, question_text, expected_output_query, explanation)
VALUES
('DDL', 'Create a table named "projects" with columns "id" (INTEGER) and "title" (TEXT).',
 'CREATE TABLE projects (id INTEGER, title TEXT);',
 'This is a basic CREATE TABLE statement to define a table structure.'),
('DDL', 'Alter the "employees" table to add a column "joining_date" (DATE).',
 'ALTER TABLE employees ADD COLUMN joining_date DATE;',
 'This ALTER TABLE statement adds a new column to the existing table.'),
('DML', 'Insert a new employee with id=5, name="Eve", age=28, department="Marketing", salary=6000.',
 'INSERT INTO employees (id, name, age, department, salary) VALUES (5, "Eve", 28, "Marketing", 6000);',
 'This INSERT statement adds a new row to the employees table.'),
('DML', 'Update the salary of "Bob" to 7500.',
 'UPDATE employees SET salary = 7500 WHERE name = "Bob";',
 'This UPDATE statement modifies the salary for the specified employee.'),
('DCL', 'Grant SELECT privilege on the "employees" table to user "manager".',
 'GRANT SELECT ON employees TO manager;',
 'This GRANT statement provides SELECT access to a user on a specific table.'),
('Miscellaneous', 'Select all employees from the "Engineering" department.',
 'SELECT * FROM employees WHERE department = "Engineering";',
 'This SELECT statement retrieves all rows where the department is "Engineering".'),
('Miscellaneous', 'Calculate the average salary of employees.',
 'SELECT AVG(salary) AS average_salary FROM employees;',
 'This SELECT statement uses an aggregate function to calculate the average salary.');
