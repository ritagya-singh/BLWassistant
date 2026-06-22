import sys
import os
import sqlite3
import random
import bcrypt
import csv

from faker import Faker
from datetime import datetime

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from data.departments import DEPARTMENTS
from data.designations import DESIGNATIONS
from data.pay_levels import PAY_LEVELS
from data.department_designations import (
    DEPARTMENT_DESIGNATIONS
)

fake = Faker("en_IN")

conn = sqlite3.connect("database/railway_pf.db")
cursor = conn.cursor()

NUM_EMPLOYEES = 10

os.makedirs("demo_data", exist_ok=True)

credential_file = open(
    "demo_data/employee_credentials.csv",
    "w",
    newline=""
)

writer = csv.writer(credential_file)

writer.writerow([
    "employee_id",
    "name",
    "pin"
])

for i in range(NUM_EMPLOYEES):

    employee_id = f"RW{1001 + i}"

    name = fake.name()

    department = random.choice(
        DEPARTMENTS
    )

    designation = random.choice(
        DEPARTMENT_DESIGNATIONS[
            department
        ]
    )

    pay_level = DESIGNATIONS[
        designation
    ]

    basic_pay = PAY_LEVELS[
        pay_level
    ]

    city_classification = random.choice(
        ["X", "Y", "Z"]
    )

    date_of_joining = fake.date_between(
        start_date="-20y",
        end_date="today"
    )

    pin = str(
        random.randint(1000, 9999)
    )

    pin_hash = bcrypt.hashpw(
        pin.encode(),
        bcrypt.gensalt()
    ).decode()

    email = (
        name.lower()
        .replace(" ", ".")
        + "@blwrail.in"
    )

    writer.writerow([
        employee_id,
        name,
        pin
    ])

    # ----------------------
    # Salary Calculations
    # ----------------------

    da_percentage = 55

    da_amount = (
        basic_pay *
        da_percentage / 100
    )

    hra_rates = {
        "X": 27,
        "Y": 18,
        "Z": 9
    }

    hra_percentage = hra_rates[
        city_classification
    ]

    hra_amount = (
        basic_pay *
        hra_percentage / 100
    )

    if pay_level >= 6:
        transport_allowance = 3600
    else:
        transport_allowance = 1800

    gross_salary = (
        basic_pay +
        da_amount +
        hra_amount +
        transport_allowance
    )

    pf_percentage = 12

    pf_deduction = (
        (
            basic_pay +
            da_amount
        )
        * pf_percentage / 100
    )

    professional_tax = 200

    medical_deduction = 300

    net_salary = (
        gross_salary
        - pf_deduction
        - professional_tax
        - medical_deduction
    )

    years_of_service = (
        (
            datetime.now().date()
            - date_of_joining
        ).days
        / 365
    )

    monthly_contribution = (
        pf_deduction
    )

    pf_balance = (
        monthly_contribution
        * years_of_service
        * 12
    )

    # ----------------------
    # Employees Table
    # ----------------------

    cursor.execute(
        """
        INSERT INTO employees
        (
            employee_id,
            name,
            pin_hash,
            designation,
            department,
            pay_level,
            city_classification,
            date_of_joining,
            email
        )
        VALUES
        (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            employee_id,
            name,
            pin_hash,
            designation,
            department,
            pay_level,
            city_classification,
            date_of_joining,
            email
        )
    )

    # ----------------------
    # Salary Structure Table
    # ----------------------

    cursor.execute(
        """
        INSERT INTO salary_structure
        (
            employee_id,
            basic_pay,
            da_percentage,
            da_amount,
            hra_percentage,
            hra_amount,
            transport_allowance,
            gross_salary,
            pf_percentage,
            professional_tax,
            medical_deduction,
            net_salary
        )
        VALUES
        (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            employee_id,
            basic_pay,
            da_percentage,
            da_amount,
            hra_percentage,
            hra_amount,
            transport_allowance,
            gross_salary,
            pf_percentage,
            professional_tax,
            medical_deduction,
            net_salary
        )
    )

    # ----------------------
    # PF Account Table
    # ----------------------

    cursor.execute(
        """
        INSERT INTO pf_account
        (
            employee_id,
            monthly_contribution,
            pf_balance,
            last_updated
        )
        VALUES
        (?, ?, ?, ?)
        """,
        (
            employee_id,
            monthly_contribution,
            round(
                pf_balance,
                2
            ),
            datetime.now().date()
        )
    )

    # ----------------------
    # Salary History
    # ----------------------

    for month in range(1, 13):

        gross = (
            gross_salary
            + random.randint(
                -500,
                500
            )
        )

        net = (
            net_salary
            + random.randint(
                -300,
                300
            )
        )

        cursor.execute(
            """
            INSERT INTO salary_history
            (
                employee_id,
                month,
                year,
                gross_salary,
                net_salary
            )
            VALUES
            (?, ?, ?, ?, ?)
            """,
            (
                employee_id,
                month,
                2025,
                round(
                    gross,
                    2
                ),
                round(
                    net,
                    2
                )
            )
        )

    # ----------------------
    # PF Transactions
    # ----------------------

    running_balance = 0

    for month in range(1, 13):

        contribution = (
            monthly_contribution
        )

        interest = round(
            contribution * 0.08,
            2
        )

        running_balance += (
            contribution +
            interest
        )

        cursor.execute(
            """
            INSERT INTO pf_transactions
            (
                employee_id,
                month,
                year,
                contribution,
                interest_credited,
                balance_after_credit
            )
            VALUES
            (?, ?, ?, ?, ?, ?)
            """,
            (
                employee_id,
                month,
                2025,
                contribution,
                interest,
                round(
                    running_balance,
                    2
                )
            )
        )

credential_file.close()

conn.commit()
conn.close()

print(
    "Employees, Salary History and PF Transactions inserted successfully!"
)