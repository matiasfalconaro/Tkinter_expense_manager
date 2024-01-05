import datetime
import locale
import logging
import re

from tkinter.messagebox import showinfo

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
            self.view.update_status_bar("Quantity and amount must be positive numbers.")
            return False

        return True

    def prepare_data(self) -> dict:
        due_date_value = (
            'N/A' if self.view.var_check_due_date.get()
            else self.view.e_due_date.get_date().strftime("%Y-%m-%d")
        )

        self.view.var_due_date.set(due_date_value)
        self.view.var_date.set(self.view.cal_date.get_date().strftime("%Y-%m-%d"))

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
            if not purchase_id:
                showinfo("Info", "You must select a record to delete.")
                self.view.update_status_bar(
                    "You must select a record to delete."
                )
                self.cancel()
                return

            db_id_str = self.view.tree.item(purchase_id, 'text')

            if re.match(r'^\d+$', db_id_str):  # Integers >= 0
                db_id = int(db_id_str)
            else:
                showinfo("Error",  "The ID is not a valid number.")
                self.view.update_status_bar("The ID is not a valid number.")
                self.cancel()
                return

            self.model.delete_from_db(db_id)
            self.view.tree.delete(purchase_id)
            self.view.load_total_accumulated()
            self.view.update_status_bar(
                "Record deleted with ID: " + str(db_id)
            )
            self.confirm()
        except Exception as e:
            self.view.update_status_bar(f"Error deleting record: {e}")

    def modify(self) -> None:
        """Prepares the form for modifying the selected record
        by loading its values into the input fields."""
        try:
            purchase_id = self.view.tree.focus()
            if not purchase_id:
                showinfo("Info", "You must select a record to modify.")
                self.view.update_status_bar(
                    "You must select a record to modify."
                )
                self.cancel()
                return

            db_id_str = self.view.tree.item(purchase_id, 'text')
            db_id = int(db_id_str)  # Potential ValueError

            values = self.view.tree.item(purchase_id, 'values')
            if len(values) < 10:
                raise ValueError("Incomplete data for the selected record.")

            self.view.var_product.set(values[0])
            self.view.var_quantity.set(values[1])
            self.view.var_amount.set(values[2])
            self.view.var_date.set(values[8])
            self.view.cb_responsible.set(values[3])
            self.view.cb_category.set(values[5])
            self.view.cb_payment_method.set(values[7])
            self.view.var_supplier.set(values[6])
            self.view.var_due_date.set(values[9])

            self.view.update_status_bar("Modifying record ID: " + str(db_id))

            self.view.confirm_button.config(
                state='normal',
                command=lambda: self.apply_modification(
                    purchase_id,
                    db_id)
            )
            self.view.cancel_button.config(state='normal')
        except ValueError as e:
            showinfo("Error", f"Data error: {e}")
            self.view.update_status_bar(f"Data error: {e}")
            self.cancel()
        except Exception as e:
            showinfo("Error", f"Unexpected error: {e}")
            self.view.update_status_bar(f"Unexpected error: {e}")
            self.cancel()

    def search(self) -> None:
        """Searches the database records based on the given search term
        and updates the treeview with the filtered results."""
        try:
            search_term = self.view.var_search.get()
            search_term = "" if "*" in search_term else search_term

            records = self.model.query_db()

            regex = re.compile(search_term, re.IGNORECASE)

            filtered_records = [
                row for row in records
                if regex.search(' '.join(map(str, row)))
            ]

            for i in self.view.tree.get_children():
                self.view.tree.delete(i)

            for row in filtered_records:
                self.view.tree.insert('',
                                      'end',
                                      text=str(row[0]),
                                      values=row[1:])

            status_message = (
                "All records are shown." if search_term == ""
                else f"Search results for: {search_term}"
            )
            self.view.update_status_bar(status_message)

            self.view.load_total_accumulated()
        except Exception as e:
            self.view.update_status_bar(f"Error in search operation: {e}")

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
        """Applies modifications to a purchase record if all fields are valid;
        otherwise, displays an error and resets the form."""
        try:
            if not self.validate_fields():
                self.view.update_status_bar("All fields must be filled.")
                showinfo("Info", "All fields must be filled.")
                self.cancel()
                return

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

            self.model.update_db(db_id, new_value)

            if self.view.tree.exists(purchase_id):
                self.view.tree.item(purchase_id, values=(
                    new_value['product_service'],
                    new_value['quantity'],
                    new_value['amount'],
                    new_value['responsible'],
                    new_value['amount'] * new_value['quantity'],  # Subtotal
                    new_value['category'],
                    new_value['supplier'],
                    new_value['payment_method'],
                    new_value['date'],
                    new_value['due_date']
                ))

            self.view.update_status_bar(
                "Record modified with ID: " + str(db_id)
            )
            self.view.load_total_accumulated()
            self.view.clear_form()
            self.confirm()
        except Exception as e:
            self.view.update_status_bar(f"Error modifying record: {e}")

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
