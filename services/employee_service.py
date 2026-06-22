import sqlite3

DB_PATH = "database/railway_pf.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def get_employee_greeting_info(employee_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            employee_id,
            name,
            designation,
            department,
            city_classification,
            date_of_joining
        FROM employees
        WHERE employee_id = ?
    """, (employee_id,))

    employee = cursor.fetchone()

    conn.close()

    return employee


def get_salary_structure(employee_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM salary_structure
        WHERE employee_id = ?
    """, (employee_id,))

    salary = cursor.fetchone()

    conn.close()

    return salary


def get_pf_details(employee_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM pf_account
        WHERE employee_id = ?
    """, (employee_id,))

    pf = cursor.fetchone()

    conn.close()

    return pf