# data.py — BLW Employee Database
EMPLOYEES = {
    "BLW001": {
        "name": "Rajesh Kumar Singh",
        "designation": "Senior Loco Pilot",
        "department": "Operations",
        "grade": "GP-4600",
        "basic": 45000, "da": 27000, "hra": 9000, "ta": 3600,
        "pf": 6300, "pf_employer": 6300,
        "income_tax": 2800, "esi": 0, "other": 500,
        "account_no": "XXXX XXXX 4521", "bank": "SBI Varanasi",
    },
    "BLW002": {
        "name": "Priya Sharma",
        "designation": "Junior Engineer (Electrical)",
        "department": "Electrical Maintenance",
        "grade": "GP-4200",
        "basic": 38000, "da": 22800, "hra": 7600, "ta": 3200,
        "pf": 5320, "pf_employer": 5320,
        "income_tax": 1800, "esi": 0, "other": 300,
        "account_no": "XXXX XXXX 7834", "bank": "Bank of Baroda",
    },
    "BLW003": {
        "name": "Mohan Lal Verma",
        "designation": "Technician Grade-I",
        "department": "Manufacturing",
        "grade": "GP-2800",
        "basic": 28000, "da": 16800, "hra": 5600, "ta": 2800,
        "pf": 3920, "pf_employer": 3920,
        "income_tax": 800, "esi": 0, "other": 200,
        "account_no": "XXXX XXXX 3310", "bank": "PNB Varanasi",
    },
    "BLW004": {
        "name": "Sunita Devi",
        "designation": "Office Superintendent",
        "department": "Administration",
        "grade": "GP-4200",
        "basic": 40000, "da": 24000, "hra": 8000, "ta": 3400,
        "pf": 5600, "pf_employer": 5600,
        "income_tax": 2100, "esi": 0, "other": 400,
        "account_no": "XXXX XXXX 6621", "bank": "Canara Bank",
    },
    "BLW005": {
        "name": "Amit Pandey",
        "designation": "Artisan Grade-I (Fitter)",
        "department": "Production",
        "grade": "GP-2400",
        "basic": 24000, "da": 14400, "hra": 4800, "ta": 2400,
        "pf": 3360, "pf_employer": 3360,
        "income_tax": 0, "esi": 300, "other": 150,
        "account_no": "XXXX XXXX 9043", "bank": "UCO Bank",
    },
    "BLW006": {
        "name": "Vikram Chauhan",
        "designation": "Assistant Divisional Engineer",
        "department": "Civil Engineering",
        "grade": "GP-4800",
        "basic": 52000, "da": 31200, "hra": 10400, "ta": 4000,
        "pf": 7280, "pf_employer": 7280,
        "income_tax": 5200, "esi": 0, "other": 600,
        "account_no": "XXXX XXXX 1155", "bank": "SBI Varanasi",
    },
    "BLW007": {
        "name": "Kavita Mishra",
        "designation": "Section Engineer (Mechanical)",
        "department": "Mechanical",
        "grade": "GP-4600",
        "basic": 48000, "da": 28800, "hra": 9600, "ta": 3800,
        "pf": 6720, "pf_employer": 6720,
        "income_tax": 3600, "esi": 0, "other": 450,
        "account_no": "XXXX XXXX 2278", "bank": "Axis Bank",
    },
    "BLW008": {
        "name": "Suresh Yadav",
        "designation": "Khalasi Helper",
        "department": "General Services",
        "grade": "GP-1800",
        "basic": 18000, "da": 10800, "hra": 3600, "ta": 1800,
        "pf": 2520, "pf_employer": 2520,
        "income_tax": 0, "esi": 225, "other": 100,
        "account_no": "XXXX XXXX 5567", "bank": "India Post Bank",
    },
}
def lookup_employee(service_number: str, provided_name: str) -> dict:
    """Return employee dict on match, or error dict."""
    svc = service_number.strip().upper()
    emp = EMPLOYEES.get(svc)
    if not emp:
        return {"error": "not_found"}
    stored  = emp["name"].lower()
    given   = provided_name.strip().lower()
    first   = given.split()[0] if given else ""
    name_ok = (
        given in stored
        or stored in given
        or any(w.startswith(first) for w in stored.split())
    )
    if not name_ok:
        return {"error": "name_mismatch"}
    return {"error": None, "employee": emp}
