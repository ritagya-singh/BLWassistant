"""
db_lookup.py — connects to the real SQLite database (database/railway_pf.db)
"""

import os
import sqlite3
import bcrypt
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "database", "railway_pf.db")


def _get_conn():
    return sqlite3.connect(DB_PATH)


def lookup_employee(employee_id: str, pin: str) -> dict:
    employee_id = employee_id.strip().upper()
    pin = pin.strip()

    conn = _get_conn()
    cur  = conn.cursor()

    # 1. Check lockout
    cur.execute("""
        SELECT status FROM login_audit
        WHERE employee_id = ?
        ORDER BY id DESC LIMIT 3
    """, (employee_id,))
    recent = [r[0] for r in cur.fetchall()]
    if recent and all(s == "FAILED" for s in recent) and len(recent) >= 3:
        conn.close()
        return {"error": "locked"}

    # 2. Fetch employee record
    cur.execute("""
        SELECT employee_id, name, pin_hash, designation,
               department, pay_level, city_classification,
               date_of_joining, email
        FROM employees
        WHERE employee_id = ?
    """, (employee_id,))
    emp_row = cur.fetchone()

    if emp_row is None:
        conn.close()
        return {"error": "not_found"}

    # 3. Verify PIN
    stored_hash = emp_row[2]
    pin_ok = bcrypt.checkpw(pin.encode(), stored_hash.encode())

    cur.execute("""
        INSERT INTO login_audit (employee_id, login_time, status)
        VALUES (?, ?, ?)
    """, (employee_id, datetime.now(), "SUCCESS" if pin_ok else "FAILED"))
    conn.commit()

    if not pin_ok:
        cur.execute("""
            SELECT status FROM login_audit
            WHERE employee_id = ?
            ORDER BY id DESC LIMIT 3
        """, (employee_id,))
        recent2 = [r[0] for r in cur.fetchall()]
        fails   = sum(1 for s in recent2 if s == "FAILED")
        remaining = max(0, 3 - fails)
        conn.close()
        return {"error": "wrong_pin", "remaining": remaining}

    # 4. Fetch salary structure
    cur.execute("""
        SELECT basic_pay, da_percentage, da_amount,
               hra_percentage, hra_amount, transport_allowance,
               gross_salary, pf_percentage, professional_tax,
               medical_deduction, net_salary
        FROM salary_structure
        WHERE employee_id = ?
    """, (employee_id,))
    sal = cur.fetchone()

    # 5. Fetch PF account
    cur.execute("""
        SELECT monthly_contribution, pf_balance, last_updated
        FROM pf_account
        WHERE employee_id = ?
    """, (employee_id,))
    pf = cur.fetchone()

    conn.close()

    employee = {
        "employee_id":     emp_row[0],
        "name":            emp_row[1],
        "designation":     emp_row[3],
        "department":      emp_row[4],
        "pay_level":       emp_row[5],
        "city_class":      emp_row[6],
        "date_of_joining": emp_row[7],
        "email":           emp_row[8] or "—",
        "grade":           "Pay Level " + str(emp_row[5]),
        "basic":           int(sal[0])  if sal else 0,
        "da":              int(sal[2])  if sal else 0,
        "hra":             int(sal[4])  if sal else 0,
        "ta":              int(sal[5])  if sal else 0,
        "gross":           int(sal[6])  if sal else 0,
        "pf":              int((sal[0] * sal[7] / 100)) if sal else 0,
        "income_tax":      int(sal[8])  if sal else 0,
        "esi":             int(sal[9])  if sal else 0,
        "other":           0,
        "net":             int(sal[10]) if sal else 0,
        "pf_monthly":      int(pf[0])   if pf else 0,
        "pf_balance":      int(pf[1])   if pf else 0,
        "pf_employer":     int(pf[0])   if pf else 0,
        "pf_last_updated": pf[2]        if pf else "—",
        "account_no":      "XXXXXXXX" + employee_id[-4:],
        "bank":            "State Bank of India",
    }

    return {"error": None, "employee": employee}