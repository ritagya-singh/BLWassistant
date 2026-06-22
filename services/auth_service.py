import sqlite3
import bcrypt
from datetime import datetime

DB_PATH = "database/railway_pf.db"

MAX_FAILED_ATTEMPTS = 3


def get_connection():
    return sqlite3.connect(DB_PATH)


def log_login_attempt(employee_id, status):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO login_audit
        (
            employee_id,
            login_time,
            status
        )
        VALUES (?, ?, ?)
    """, (
        employee_id,
        datetime.now(),
        status
    ))

    conn.commit()
    conn.close()


def get_failed_attempts(employee_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT status
        FROM login_audit
        WHERE employee_id = ?
        ORDER BY id DESC
        LIMIT 3
    """, (employee_id,))

    rows = cursor.fetchall()

    conn.close()

    count = 0

    for row in rows:
        if row[0] == "FAILED":
            count += 1
        else:
            break

    return count


def is_locked_out(employee_id):

    failed_attempts = get_failed_attempts(
        employee_id
    )

    return failed_attempts >= MAX_FAILED_ATTEMPTS


def verify_pin(employee_id, entered_pin):

    if is_locked_out(employee_id):

        return {
            "success": False,
            "message": "Account Locked"
        }

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT pin_hash
        FROM employees
        WHERE employee_id = ?
    """, (employee_id,))

    result = cursor.fetchone()

    conn.close()

    if result is None:

        return {
            "success": False,
            "message": "Employee Not Found"
        }

    stored_hash = result[0]

    is_valid = bcrypt.checkpw(
        entered_pin.encode(),
        stored_hash.encode()
    )

    if is_valid:

        log_login_attempt(
            employee_id,
            "SUCCESS"
        )

        return {
            "success": True,
            "message": "Login Successful"
        }

    else:

        log_login_attempt(
            employee_id,
            "FAILED"
        )

        remaining = (
            MAX_FAILED_ATTEMPTS
            - get_failed_attempts(employee_id)
        )

        return {
            "success": False,
            "message": f"Invalid PIN. {remaining} attempts remaining."
        }