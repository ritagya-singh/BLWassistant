CREATE TABLE employees (
    employee_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    pin_hash TEXT NOT NULL,
    designation TEXT NOT NULL,
    department TEXT NOT NULL,
    pay_level INTEGER NOT NULL,
    city_classification TEXT NOT NULL,
    date_of_joining DATE NOT NULL,
    email TEXT
);
CREATE TABLE salary_structure (
    employee_id TEXT PRIMARY KEY,

    basic_pay REAL,
    da_percentage REAL,
    da_amount REAL,

    hra_percentage REAL,
    hra_amount REAL,

    transport_allowance REAL,

    gross_salary REAL,

    pf_percentage REAL,

    professional_tax REAL,
    medical_deduction REAL,

    net_salary REAL,

    FOREIGN KEY(employee_id)
    REFERENCES employees(employee_id)
);
CREATE TABLE pf_account (
    employee_id TEXT PRIMARY KEY,

    monthly_contribution REAL,

    pf_balance REAL,

    last_updated DATE,

    FOREIGN KEY(employee_id)
    REFERENCES employees(employee_id)
);
CREATE TABLE salary_history (
    history_id INTEGER PRIMARY KEY AUTOINCREMENT,

    employee_id TEXT,

    month INTEGER,
    year INTEGER,

    gross_salary REAL,
    net_salary REAL,

    FOREIGN KEY(employee_id)
    REFERENCES employees(employee_id)
);
CREATE TABLE pf_transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,

    employee_id TEXT,

    month INTEGER,
    year INTEGER,

    contribution REAL,
    interest_credited REAL,

    balance_after_credit REAL,

    FOREIGN KEY(employee_id)
    REFERENCES employees(employee_id)
);
CREATE TABLE login_audit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    employee_id TEXT,

    login_time DATETIME,

    status TEXT
);