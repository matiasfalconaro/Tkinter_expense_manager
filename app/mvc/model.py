import sqlite3

from typing import Optional, List, Tuple

from controller import get_current_month


# DATABASE
def connect_to_database() -> sqlite3.Connection:
    """Establishes and returns a connection to the SQLite database."""
    conn = sqlite3.connect('database/database.db')
    return conn


def disconnect_from_database(conn: sqlite3.Connection) -> None:
    """Closes the given database connection."""
    conn.close()


def create_table(conn: sqlite3.Connection) -> None:
    """Creates the 'expenses' table in the database
    if it does not already exist."""
    cursor = conn.cursor()
    query = """CREATE TABLE IF NOT EXISTS expenses (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               product_service TEXT,
               quantity INTEGER,
               amount FLOAT,
               responsible TEXT,
               subtotal FLOAT,
               category TEXT,
               supplier TEXT,
               payment_method TEXT,
               date DATE,
               due_date DATE
               );"""
    cursor.execute(query)
    conn.commit()


def add_to_db(conn: sqlite3.Connection, values: dict) -> int:
    """Inserts a new record into the 'expenses' table
    and returns the ID of the inserted record."""
    conn = connect_to_database()
    cursor = conn.cursor()

    query = """INSERT INTO expenses (product_service,
               quantity,
               amount,
               responsible,
               subtotal,
               category, supplier,
               payment_method,
               date,
               due_date)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""

    subtotal = values['quantity'] * values['amount']

    data = (values['product'],
            values['quantity'],
            values['amount'],
            values['responsible'],
            subtotal, values['category'],
            values['supplier'],
            values['payment_method'],
            values['date'],
            values['due_date'])

    cursor.execute(query, data)
    conn.commit()
    last_id = cursor.lastrowid
    disconnect_from_database(conn)
    return last_id


def delete_from_db(record_id: int) -> None:
    """Deletes a record from the 'expenses' table
    based on the given record ID."""
    conn = connect_to_database()
    cursor = conn.cursor()
    query = "DELETE FROM expenses WHERE id = ?;"
    cursor.execute(query, (record_id,))
    conn.commit()
    disconnect_from_database(conn)


def update_db(record_id: int, values: dict) -> None:
    """Updates a specific record in the 'expenses' table
    with new values based on the given record ID."""
    conn = connect_to_database()
    cursor = conn.cursor()
    query = """UPDATE expenses SET
               product_service = ?,
               quantity = ?,
               amount = ?,
               responsible = ?,
               subtotal = ?,
               category = ?,
               supplier = ?,
               payment_method = ?,
               date = ?,
               due_date = ?
               WHERE id = ?;"""

    subtotal = int(values['quantity'] * values['amount'] * 100) / 100.0
    data = (values['product'],
            values['quantity'],
            values['amount'],
            values['responsible'],
            subtotal, values['category'],
            values['supplier'],
            values['payment_method'],
            values['date'],
            values['due_date'],
            record_id)

    cursor.execute(query, data)
    conn.commit()
    disconnect_from_database(conn)


def query_db(month: Optional[int] = None) -> List[Tuple]:
    """Queries and returns records from the 'expenses' table,
    optionally filtering by the specified month."""
    conn = connect_to_database()
    cursor = conn.cursor()
    if month is not None:
        query = """SELECT subtotal
                   FROM expenses WHERE strftime('%m', date) = ?;"""
        cursor.execute(query, (f"{month:02d}",))
    else:
        query = """SELECT * FROM expenses;"""
        cursor.execute(query)
    rows = cursor.fetchall()
    disconnect_from_database(conn)
    return rows


# Establish a connection to the SQLite database.
conn = connect_to_database()

# Create the 'expenses' table in the database if it does not already exist.
create_table(conn)
# END DATABASE


# GRAPH (DATA)
def get_graph_data() -> List[Tuple]:
    """Retrieves and returns data for graph generation
    based on categories and their subtotals for the current month."""
    conn = connect_to_database()
    cursor = conn.cursor()

    current_month_num = get_current_month()
    if (not isinstance(current_month_num, int)
            or not (1 <= current_month_num <= 12)):
        print("Invalid month number.")
        disconnect_from_database(conn)
        return []

    formatted_month = f"{current_month_num:02d}"  # Format as two-digit month

    query = f"""SELECT category, SUM(subtotal)
                FROM expenses
                WHERE strftime('%m', date) = '{formatted_month}'
                GROUP BY category"""

    cursor.execute(query)
    data = cursor.fetchall()

    disconnect_from_database(conn)
    return data
# END GRAPH (DATA)
