import sqlite3

from typing import Optional, List, Tuple


class Model:
    """Handles database operations"""
    def __init__(self):
        self.conn = self.connect_to_database()

    def connect_to_database(self) -> sqlite3.Connection:
        """Establishes and returns a connection to the SQLite database."""
        return sqlite3.connect('database/database.db')

    def disconnect_from_database(self) -> None:
        """Closes the database connection."""
        self.conn.close()

    def create_table(self) -> None:
        """Creates the 'expenses' table in the database
        if it does not already exist."""
        cursor = self.conn.cursor()
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
        self.conn.commit()

    def add_to_db(self, values: dict) -> int:
        """Inserts a new record into the 'expenses' table
        and returns the ID of the inserted record."""
        try:
            cursor = self.conn.cursor()
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
            self.conn.commit()
            last_id = cursor.lastrowid
            return last_id
        except sqlite3.DatabaseError as e:
            print(f"Database error: {e}")
            self.conn.rollback()
            return -1

    def delete_from_db(self, record_id: int) -> None:
        """Deletes a record from the 'expenses' table
        based on the given record ID."""
        try:
            cursor = self.conn.cursor()
            query = "DELETE FROM expenses WHERE id = ?;"
            cursor.execute(query, (record_id,))
            self.conn.commit()
        except sqlite3.DatabaseError as e:
            print(f"Database error: {e}")
            self.conn.rollback()
            # Optionally, re-raise the exception

    def update_db(self, record_id: int, values: dict) -> None:
        """Updates a specific record in the 'expenses' table
        with new values based on the given record ID."""
        try:
            cursor = self.conn.cursor()
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
            self.conn.commit()
        except sqlite3.DatabaseError as e:
            print(f"Database error: {e}")
            self.conn.rollback()
            # Optionally, re-raise the exception

    def query_db(self, month: Optional[int] = None) -> List[Tuple]:
        """Queries and returns records from the 'expenses' table,
        optionally filtering by the specified month."""
        try:
            cursor = self.conn.cursor()
            if month is not None:
                query = """SELECT subtotal
                        FROM expenses WHERE strftime('%m', date) = ?;"""
                cursor.execute(query, (f"{month:02d}",))
            else:
                query = """SELECT * FROM expenses;"""
                cursor.execute(query)
            rows = cursor.fetchall()
            return rows
        except sqlite3.DatabaseError as e:
            print(f"Database error: {e}")
            # Handle the error as appropriate
            return []

    def get_graph_data(self, get_current_month: int) -> List[Tuple]:
        """Retrieves and returns data for graph generation
        based on categories and their subtotals for the current month."""
        try:
            cursor = self.conn.cursor()

            # Ensure function is available
            current_month_num = get_current_month
            if not (isinstance(current_month_num, int)
                    and 1 <= current_month_num <= 12):
                print("Invalid month number.")
                return []

            formatted_month = f"{current_month_num:02d}"

            query = f"""SELECT category, SUM(subtotal)
                        FROM expenses
                        WHERE strftime('%m', date) = '{formatted_month}'
                        GROUP BY category"""

            cursor.execute(query)
            data = cursor.fetchall()
            return data
        except sqlite3.DatabaseError as e:
            print(f"Database error: {e}")
            return []
