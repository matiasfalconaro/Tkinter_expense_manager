import logging
import sqlite3

from typing import Optional, List, Tuple


class Model:
    """Handles database operations"""
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.conn = self.connect_to_database()

    def connect_to_database(self) -> sqlite3.Connection:
        """Establishes and returns a connection to the SQLite database."""
        try:
            conn = sqlite3.connect('database/database.db')
            self.logger.info("Database connection established.")
            return conn
        except sqlite3.Error as e:
            self.logger.error(f"Database connection error: {e}")
            raise

    def disconnect_from_database(self) -> None:
        """Closes the database connection."""
        try:
            self.conn.close()
            self.logger.info("Database connection closed.")
        except sqlite3.Error as e:
            self.logger.error(f"Database disconnection error: {e}")

    def create_table(self) -> None:
        """Creates the 'expenses' table in the database
        if it does not already exist."""
        try:
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
            self.logger.info("Table 'expenses' created or already exists.")
        except sqlite3.DatabaseError as e:
            self.logger.error(f"Database error: {e}")

    def add_to_db(self, values: dict) -> int:
        """Inserts a new expense record into the database
        after validating the input data."""
        try:
            if not self.validate_expense_data(values):
                return -1

            cursor = self.conn.cursor()
            query = """INSERT INTO expenses (
                    product_service,
                    quantity,
                    amount,
                    responsible,
                    subtotal,
                    category,
                    supplier,
                    payment_method,
                    date,
                    due_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""

            subtotal = round(values['quantity'] * values['amount'], 2)
            data = (values['product'],
                    values['quantity'],
                    values['amount'],
                    values['responsible'],
                    subtotal,
                    values['category'],
                    values['supplier'],
                    values['payment_method'],
                    values['date'],
                    values['due_date'])

            cursor.execute(query, data)
            self.conn.commit()
            last_id = cursor.lastrowid
            return last_id

        except ValueError as e:
            self.logger.error(f"Input validation error: {e}")
            return -1
        except sqlite3.DatabaseError as e:
            self.logger.error(f"Database error: {e}")
            self.conn.rollback()
            return -1

    def validate_expense_data(self, values: dict) -> bool:
        """Validates the provided expense data
        against required fields and types."""
        required_fields = ['product',
                           'quantity',
                           'amount',
                           'responsible',
                           'category',
                           'supplier',
                           'payment_method',
                           'date',
                           'due_date']
        for field in required_fields:
            if field not in values or values[field] is None:
                self.logger.error(f"Missing required field: {field}")
                raise ValueError(f"Missing required field: {field}")

        if (
            not isinstance(values['quantity'], (int, float))
            or not isinstance(values['amount'], (float, int))
        ):
            self.logger.error("Quantity and amount must be numeric")
            raise ValueError("Quantity and amount must be numeric")

        return True

    def delete_from_db(self, record_id: int) -> bool:
        """Deletes a record from the 'expenses' table
        based on the given record ID."""
        try:
            if not isinstance(record_id, int) or record_id <= 0:
                raise ValueError("Invalid record ID.")

            cursor = self.conn.cursor()

            select_query = "SELECT * FROM expenses WHERE id = ?;"
            cursor.execute(select_query, (record_id,))
            record = cursor.fetchone()

            if record is None:
                self.logger.warning(f"No record found with ID: {record_id}")
                return False

            self.logger.debug(f"Deleting record with ID {record_id}: {record}")

            delete_query = "DELETE FROM expenses WHERE id = ?;"
            cursor.execute(delete_query, (record_id,))
            self.conn.commit()

            return True

        except ValueError as e:
            self.logger.error(f"Input validation error: {e}")
            return False
        except sqlite3.DatabaseError as e:
            self.logger.error(f"Database error: {e}")
            self.conn.rollback()
            return False

    def update_db(self, record_id: int, values: dict) -> None:
        """Updates an existing expense record
        in the database with the provided values."""
        try:
            if not self.validate_update_data(record_id, values):
                return

            cursor = self.conn.cursor()

            values['subtotal'] = round(
                values['quantity'] * values['amount'], 2
            )
            set_clause = ', '.join([f"{key} = ?" for key in values])
            query = f"UPDATE expenses SET {set_clause} WHERE id = ?;"
            data = tuple(values.values()) + (record_id,)

            cursor.execute(query, data)
            self.conn.commit()

        except ValueError as e:
            self.logger.error(f"Input validation error: {e}")
            self.conn.rollback()
        except sqlite3.DatabaseError as e:
            self.logger.error(f"Database error: {e}")
            self.conn.rollback()

    def validate_update_data(self, record_id: int, values: dict) -> bool:
        """Validates the record ID and
        data fields for updating an expense record."""
        if not isinstance(record_id, int) or record_id <= 0:
            self.logger.error("Invalid record ID.")
            raise ValueError("Invalid record ID.")

        required_fields = ['quantity', 'amount']  # Add other fields as needed
        for field in required_fields:
            if field not in values:
                self.logger.error(
                    f"Missing required field for update: {field}"
                )
                raise ValueError(f"Missing required field for update: {field}")

        if (not isinstance(values['quantity'], (int, float)) or
                not isinstance(values['amount'], (float, int))):

            self.logger.error("Quantity and amount must be numeric for update")
            raise ValueError("Quantity and amount must be numeric for update")

        return True

    def query_db(self, month: Optional[int] = None) -> List[Tuple]:
        """Queries and returns records from the 'expenses' table,
        optionally filtering by the specified month."""
        try:
            cursor = self.conn.cursor()
            base_query = "SELECT * FROM expenses"
            params = []

            if month is not None:
                if 1 <= month <= 12:
                    base_query += " WHERE strftime('%m', date) = ?"
                    params.append(f"{month:02d}")
                else:
                    self.logger.error("Invalid month number.")
                    return []

            cursor.execute(base_query, params)
            rows = cursor.fetchall()
            return rows
        except sqlite3.DatabaseError as e:
            self.logger.error(f"Database error: {e}")
            return []

    def get_graph_data(self, get_current_month: int) -> List[Tuple]:
        """Retrieves and returns data for graph generation
        based on categories and their subtotals for the current month."""
        try:
            if (not isinstance(get_current_month, int) or
                    not 1 <= get_current_month <= 12):
                self.logger.error(f"Invalid month number: {get_current_month}")
                return []

            cursor = self.conn.cursor()
            query = """SELECT category, SUM(subtotal)
                    FROM expenses
                    WHERE strftime('%m', date) = ?
                    GROUP BY category"""

            cursor.execute(query, (f"{get_current_month:02d}",))
            data = cursor.fetchall()
            return data
        except sqlite3.DatabaseError as e:
            self.logger.error(f"Database error in get_graph_data: {e}")
            return []
