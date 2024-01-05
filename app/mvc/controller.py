import datetime
import locale
import logging
import re

from tkinter.messagebox import showinfo

from typing import List, Optional

from utils.methods import get_current_month


class Controller:
    """Manages interactions between the model and view"""

    def __init__(self, model):
        self.logger = logging.getLogger(__name__)
        self.model = model
        self.view = None

    def set_view(self, view):
        self.view = view

    def get_get_graph_data(self):
        current_month = get_current_month()
        return self.model.get_graph_data(current_month)

    def get_query_db(self, month=None):
        return self.model.query_db(month)

    def add(self) -> None:
        """Adds a new record to the database and updates the UI accordingly."""
        if not self.validate_inputs():
            return

        values = self.prepare_data()
        if not values:
            return

        try:
            last_id = self.model.add_to_db(values)
            if last_id == -1:  # Handle failure
                raise Exception("Failed to add record to the database.")

            self.update_ui_after_add(last_id, values)
            self.confirm()
        except Exception as e:
            self.view.update_status_bar(f"Error: {e}")

    def validate_inputs(self) -> bool:
        """Validates user inputs from the form,
        ensuring all fields are correctly filled."""
        if (not self.view.var_product.get() or
                not self.view.var_quantity.get() or
                not self.view.var_amount.get() or
                not self.view.cb_responsible.get()):
            self.view.update_status_bar("All input fields must be completed")
            showinfo("Info", "All input fields must be completed")
            return False

        quantity = int(self.view.var_quantity.get())
        amount = float(self.view.var_amount.get())
        if quantity <= 0 or amount <= 0:
            self.view.update_status_bar(
                "Quantity and amount must be positive numbers."
            )
            return False

        return True

    def prepare_data(self) -> dict:
        """Prepares and returns a dictionary of data
        extracted from the form inputs."""
        due_date_value = (
            'N/A' if self.view.var_check_due_date.get()
            else self.view.e_due_date.get_date().strftime("%Y-%m-%d")
        )

        self.view.var_due_date.set(due_date_value)
        self.view.var_date.set(
            self.view.cal_date.get_date().strftime("%Y-%m-%d")
        )

        values = {
            'amount': float(self.view.var_amount.get()),
            'product': self.view.var_product.get(),
            'category': self.view.cb_category.get(),
            'date': self.view.var_date.get(),
            'supplier': self.view.var_supplier.get(),
            'payment_method': self.view.cb_payment_method.get(),
            'responsible': self.view.cb_responsible.get(),
            'quantity': int(self.view.var_quantity.get()),
            'due_date': due_date_value
        }

        return values

    def update_ui_after_add(self, last_id: int, values: dict) -> None:
        """Updates the UI components
        to reflect the addition of a new record."""
        subtotal_accumulated = round(values['quantity'] * values['amount'], 2)
        self.view.tree.insert('',
                              'end',
                              text=str(last_id),
                              values=(values['product'],
                                      values['quantity'],
                                      values['amount'],
                                      values['responsible'],
                                      f"{subtotal_accumulated:.2f}",
                                      values['category'],
                                      values['supplier'],
                                      values['payment_method'],
                                      values['date'],
                                      values['due_date']))

        self.view.load_total_accumulated()
        self.view.update_status_bar("Record added with ID: " + str(last_id))
        self.view.clear_form()

    def delete(self) -> None:
        """Deletes the selected record from the database and updates the UI."""
        try:
            purchase_id = self.view.tree.focus()
            db_id = self.validate_selection_deletion(purchase_id)
            if db_id is None:
                self.cancel()
                return

            self.model.delete_from_db(db_id)
            self.update_ui_after_delete(purchase_id, db_id)
            self.confirm()
        except Exception as e:
            self.view.update_status_bar(f"Error deleting record: {e}")

    def validate_selection_deletion(self, purchase_id: str) -> Optional[int]:
        """Validates the selected record and
        returns its database ID, or None if invalid."""
        if not purchase_id:
            showinfo("Info", "You must select a record to delete.")
            self.view.update_status_bar("You must select a record to delete.")
            return None

        db_id_str = self.view.tree.item(purchase_id, 'text')
        if re.match(r'^\d+$', db_id_str):
            return int(db_id_str)
        else:
            showinfo("Error", "The ID is not a valid number.")
            self.view.update_status_bar("The ID is not a valid number.")
            return None

    def update_ui_after_delete(self, purchase_id: str, db_id: int) -> None:
        """Updates the UI after a record deletion,
        removing it from the treeview and updating the status bar."""
        self.view.tree.delete(purchase_id)
        self.view.load_total_accumulated()
        self.view.update_status_bar("Record deleted with ID: " + str(db_id))

    def modify(self) -> None:
        """Prepares the form for modifying the selected record."""
        try:
            purchase_id = self.validate_selected_record_for_modification()
            if purchase_id is None:
                self.cancel()
                return

            self.load_data_into_form(purchase_id)
        except ValueError as e:
            showinfo("Error", f"Data error: {e}")
            self.view.update_status_bar(f"Data error: {e}")
            self.cancel()
        except Exception as e:
            showinfo("Error", f"Unexpected error: {e}")
            self.view.update_status_bar(f"Unexpected error: {e}")
            self.cancel()

    def validate_selected_record_for_modification(self) -> Optional[str]:
        """Validates if a record is selected
        for modification and returns its ID."""
        purchase_id = self.view.tree.focus()
        if not purchase_id:
            showinfo("Info", "You must select a record to modify.")
            self.view.update_status_bar("You must select a record to modify.")
            return None
        return purchase_id

    def load_data_into_form(self, purchase_id: str) -> None:
        """Loads data from the selected record into the form for editing."""
        db_id_str = self.view.tree.item(purchase_id, 'text')
        db_id = int(db_id_str)  # Potential ValueError
        values = self.view.tree.item(purchase_id, 'values')

        self.view.var_product.set(values[0])
        self.view.var_quantity.set(values[1])
        self.view.var_amount.set(values[2])
        self.view.cb_responsible.set(values[3])
        self.view.cb_category.set(values[5])
        self.view.cb_payment_method.set(values[7])
        self.view.var_supplier.set(values[6])
        self.view.var_date.set(values[8])
        self.view.var_due_date.set(values[9])

        self.view.update_status_bar("Modifying record ID: " + str(db_id))
        self.setup_modify_buttons(purchase_id, db_id)

    def setup_modify_buttons(self, purchase_id: str, db_id: int) -> None:
        """Configures the confirm and
        cancel buttons for the modify operation."""
        self.view.confirm_button.config(
            state='normal',
            command=lambda: self.apply_modification(purchase_id, db_id)
        )
        self.view.cancel_button.config(state='normal')

    def search(self) -> None:
        """Searches the database records
        and updates the treeview with filtered results."""
        try:
            search_term = self.process_search_term()
            records = self.model.query_db()
            filtered_records = self.filter_records(records, search_term)
            self.update_treeview(filtered_records)

            if not search_term:
                status_message = "All records are shown."
            else:
                status_message = f"Search results for: {search_term}"

            self.view.update_status_bar(status_message)
            self.view.load_total_accumulated()
        except Exception as e:
            self.view.update_status_bar(f"Error in search operation: {e}")

    def process_search_term(self) -> str:
        """Processes and returns the formatted search term."""
        search_term = self.view.var_search.get()
        return "" if "*" in search_term else search_term

    def filter_records(self, records, search_term: str) -> List:
        """Filters the records based on the given search term."""
        regex = re.compile(search_term, re.IGNORECASE)
        return [
            row for row in records if regex.search(' '.join(map(str, row)))
        ]

    def update_treeview(self, filtered_records):
        """Updates the treeview with the filtered records."""
        for i in self.view.tree.get_children():
            self.view.tree.delete(i)

        for row in filtered_records:
            self.view.tree.insert('', 'end', text=str(row[0]), values=row[1:])

    def validate_fields(self) -> bool:
        """Validates a set of fields,
        returning True if all fields are valid, False otherwise."""
        try:
            fields_var = [self.view.var_product,
                          self.view.var_quantity,
                          self.view.var_amount,
                          self.view.var_supplier,
                          self.view.var_date,
                          self.view.var_due_date]
            fields_cb = [self.view.cb_responsible,
                         self.view.cb_category,
                         self.view.cb_payment_method]

            for var in fields_var:
                if isinstance(var, (str, int)) and not var:
                    return False

            for cb in fields_cb:
                if not cb:
                    return False

            return True
        except Exception as e:
            self.logger.error(f"Error in validate_fields: {e}")
            return False

    def prepare_add(self) -> None:
        """Prepares the form for adding a new entry
        by enabling the confirm and cancel buttons."""
        self.view.confirm_button.config(state='normal',
                                        command=self.add)
        self.view.cancel_button.config(state='normal')

    def prepare_delete(self) -> None:
        """Prepares the form for deletion by enabling the confirm
        and cancel buttons with the delete command."""
        self.view.confirm_button.config(state='normal',
                                        command=self.delete)
        self.view.cancel_button.config(state='normal')

    def confirm(self) -> None:
        """Executes the defined action (add, delete, modify),
        disables the buttons, and updates the graph."""
        self.view.confirm_button.config(state='disabled')
        self.view.cancel_button.config(state='disabled')

        for widget in self.view.graph_frame.winfo_children():
            widget.destroy()
            self.view.create_graph(self.view.graph_frame)

    def cancel(self) -> None:
        """Disables the confirm button
        and cancel button and resets the form fields."""
        self.view.confirm_button.config(state='disabled',
                                        command=None)
        self.view.cancel_button.config(state='disabled')
        self.view.clear_form()

    def apply_modification(self, purchase_id: int, db_id: int) -> None:
        """Applies modifications to a purchase record."""
        new_value = self.validate_and_prepare_data()
        if new_value is None:
            self.cancel()
            return

        if self.update_database(db_id, new_value):
            self.update_ui_after_modify(purchase_id, new_value, db_id)
            self.view.clear_form()
            self.confirm()

    def validate_and_prepare_data(self) -> Optional[dict]:
        """Validates input fields and prepares data for database update."""
        if not self.validate_fields():
            self.view.update_status_bar("All fields must be filled.")
            showinfo("Info", "All fields must be filled.")
            return None

        new_value = {
            'product_service': self.view.var_product.get(),
            'quantity': int(self.view.var_quantity.get()),
            'amount': float(self.view.var_amount.get()),
            'responsible': self.view.cb_responsible.get(),
            'category': self.view.cb_category.get(),
            'supplier': self.view.var_supplier.get(),
            'payment_method': self.view.cb_payment_method.get(),
            'date': self.view.var_date.get(),
            'due_date': self.view.var_due_date.get()
        }
        return new_value

    def update_database(self, db_id: int, new_value: dict) -> bool:
        """Updates the database record with new values."""
        try:
            self.model.update_db(db_id, new_value)
            return True
        except Exception as e:
            self.view.update_status_bar(f"Error modifying record: {e}")
            return False

    def update_ui_after_modify(
        self, purchase_id: int, new_value: dict, db_id: int
    ) -> None:
        """Updates the UI after a successful modification."""
        if self.view.tree.exists(purchase_id):
            subtotal_accumulated = round(
                new_value['quantity'] * new_value['amount'], 2
            )

            self.view.tree.item(purchase_id, values=(
                new_value['product_service'],
                new_value['quantity'],
                new_value['amount'],
                new_value['responsible'],
                f"{subtotal_accumulated:.2f}",
                new_value['category'],
                new_value['supplier'],
                new_value['payment_method'],
                new_value['date'],
                new_value['due_date']
            ))

        self.view.update_status_bar("Record modified with ID: " + str(db_id))
        self.view.load_total_accumulated()

    def get_current_month_word(self, locale_setting=None):
        """Returns the current month's name in the specified locale.
        If no locale is specified, the system's default locale is used."""
        try:
            locale.setlocale(
                locale.LC_TIME,
                locale_setting if locale_setting else locale.getdefaultlocale()
            )

            current_month = datetime.datetime.now().month
            current_month_str = datetime.datetime.strptime(
                str(current_month), "%m"
                ).strftime("%B")

            return current_month_str.capitalize()
        except locale.Error as e:
            self.logger.error(f"Locale error: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
        return "Unknown Month"

    def get_total_accumulated(self) -> float:
        """Calculates and returns the total accumulated value
        for records in the current month."""
        try:
            current_month = get_current_month()
            records = self.model.query_db(month=current_month)

            total_accumulated = sum(row[5] for row in records)

            return total_accumulated
        except Exception as e:
            self.logger.error(f"Error in getting total accumulated: {e}")
            return 0.0
