import datetime
import locale
import re

from tkinter.messagebox import showinfo

from view import(cal_date,
                 cancel_button,
                 cb_category,
                 cb_payment_method,
                 cb_responsible,
                 confirm_button,
                 create_graph,
                 e_due_date,
                 graph_frame,
                 l_total,
                 root,
                 status,
                 tree,
                 var_amount,
                 var_category,
                 var_check_due_date,
                 var_date,
                 var_due_date,
                 var_payment_method,
                 var_product,
                 var_quantity,
                 var_responsible,
                 var_search,
                 var_supplier,
                 var_total)

from model import(query_db,
                  update_db,
                  connect_to_database,
                  add_to_db,
                  delete_from_db)


def add() -> None:
    """Adds a new record to the database and updates the UI accordingly."""
    var_date.set(cal_date.get_date().strftime("%Y-%m-%d"))
    if var_check_due_date.get():
        due_date_value = 'N/A'
    else:
        due_date_value = e_due_date.get_date().strftime("%Y-%m-%d")

    var_due_date.set(due_date_value)

    if (not var_product.get() or not var_quantity.get() or
            not var_amount.get() or not cb_responsible.get()):
        update_status_bar("All input fields must be completed")
        showinfo("Info", "All input fields must be completed")
        cancel()
        return

    values = {
        'amount': float(var_amount.get()),
        'product': var_product.get(),
        'category': cb_category.get(),
        'date': cal_date.get_date().strftime("%Y-%m-%d"),
        'supplier': var_supplier.get(),
        'payment_method': cb_payment_method.get(),
        'responsible': cb_responsible.get(),
        'quantity': int(var_quantity.get()),
        'due_date': due_date_value
    }

    for value in values.values():
        if not value:
            showinfo("Info", "All fields for add must be filled.")
            update_status_bar("All fields for add must be filled.")
            cancel()
            return

        if values['quantity'] <= 0 or values['amount'] <= 0:
            update_status_bar("Quantity and amount must be positive numbers.")
            return

    conn = connect_to_database()
    last_id = add_to_db(conn, values)

    subtotal_accumulated = round(values['quantity'] * values['amount'], 2)

    tree.insert('',
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

    load_total_accumulated()
    update_status_bar("Record added with ID: " + str(last_id))
    clear_form()
    confirm()


def delete() -> None:
    """Deletes the selected record from the database and updates the UI."""
    purchase_id = tree.focus()
    if not purchase_id:
        showinfo("Info", "You must select a record to delete.")
        update_status_bar("You must select a record to delete.")
        cancel()
        return

    db_id_str = tree.item(purchase_id, 'text')

    if re.match(r'^\d+$', db_id_str):  # Integers >= 0
        db_id = int(db_id_str)
    else:
        showinfo("Error",  "The ID is not a valid number.")
        update_status_bar("The ID is not a valid number.")
        cancel()
        return

    delete_from_db(db_id)

    tree.delete(purchase_id)
    load_total_accumulated()
    update_status_bar("Record deleted with ID: " + str(db_id))
    confirm()


def modify() -> None:
    """Prepares the form for modifying the selected record
    by loading its values into the input fields."""
    purchase_id = tree.focus()
    if not purchase_id:
        showinfo("Info", "You must select a record to modify.")
        update_status_bar("You must select a record to modify.")
        cancel()
        return

    db_id = int(tree.item(purchase_id, 'text'))

    values = tree.item(purchase_id, 'values')
    var_product.set(values[0])
    var_quantity.set(values[1])
    var_amount.set(values[2])
    var_date.set(values[8])
    cb_responsible.set(values[3])
    cb_category.set(values[5])
    cb_payment_method.set(values[7])
    var_supplier.set(values[6])
    var_due_date.set(values[9])

    update_status_bar("Modifying record ID: " + str(db_id))

    confirm_button.config(state='normal',
                          command=lambda: apply_modification(purchase_id,
                                                             db_id))
    cancel_button.config(state='normal')


def search() -> None:
    """Searches the database records based on the given search term
    and updates the treeview with the filtered results."""
    search_term = var_search.get()
    if "*" in search_term:
        search_term = ""

    records = query_db()

    regex = re.compile(search_term, re.IGNORECASE)

    filtered_records = []
    for row in records:
        row_str = ' '.join(map(str, row))
        if regex.search(row_str):
            filtered_records.append(row)

    for i in tree.get_children():
        tree.delete(i)

    for row in filtered_records:
        tree.insert('', 'end', text=str(row[0]), values=row[1:])

    if search_term == "":
        update_status_bar("All records are shown.")
    else:
        update_status_bar(f"Search results for: {search_term}")

    load_total_accumulated()
# END CRUD


def update_status_bar(message: str) -> None:
    """Updates the text of the status bar with the provided message."""
    status.config(text=message)  # Update label text
    root.update_idletasks()  # Force UI update


def update_due_date_status() -> None:
    """Enables or disables the due date entry
    based on the state of a check variable."""
    if var_check_due_date.get():
        e_due_date.config(state='disabled')
    else:
        e_due_date.config(state='normal')


def validate_fields() -> bool:
    """Validates a set of fields,
    returning True if all fields are valid, False otherwise."""
    fields_var = [var_product,
                  var_quantity,
                  var_amount,
                  var_supplier,
                  var_date,
                  var_due_date]
    fields_cb = [cb_responsible, cb_category, cb_payment_method]

    for var in fields_var:
        if isinstance(var, (str, int)) and not var:
            return False

    for cb in fields_cb:
        if not cb:
            return False

    return True


def clear_form() -> None:
    """Resets all form fields to their default (empty) values."""
    var_amount.set('')
    var_product.set('')
    var_quantity.set('')
    var_supplier.set('')
    var_responsible.set('')
    var_category.set('')
    var_payment_method.set('')
    cb_responsible.set('')
    cb_category.set('')
    cb_payment_method.set('')


def prepare_add() -> None:
    """Prepares the form for adding a new entry
    by enabling the confirm and cancel buttons."""
    confirm_button.config(state='normal',
                          command=add)
    cancel_button.config(state='normal')


def prepare_delete() -> None:
    """Prepares the form for deletion by enabling the confirm
    and cancel buttons with the delete command."""
    confirm_button.config(state='normal',
                          command=delete)
    cancel_button.config(state='normal')


def confirm() -> None:
    """Executes the defined action (add, delete, modify),
    disables the buttons, and updates the graph."""
    confirm_button.config(state='disabled')
    cancel_button.config(state='disabled')

    for widget in graph_frame.winfo_children():
        widget.destroy()  # Delete previous graphs
        create_graph(graph_frame)  # Updated graph


def cancel() -> None:
    """Disables the confirm and cancel buttons and resets the form fields."""
    confirm_button.config(state='disabled',
                          command=None)
    cancel_button.config(state='disabled')
    clear_form()


def apply_modification(purchase_id: int, db_id: int) -> None:
    """Applies modifications to a purchase record if all fields are valid;
    otherwise, displays an error and resets the form."""
    if not validate_fields():
        update_status_bar("All fields must be filled.")
        showinfo("Info", "All fields must be filled.")
        cancel()
        return

    new_value = {
        'product': var_product.get(),
        'quantity': int(var_quantity.get()),
        'amount': float(var_amount.get()),
        'responsible': cb_responsible.get(),
        'category': cb_category.get(),
        'supplier': var_supplier.get(),
        'payment_method': cb_payment_method.get(),
        'date': var_date.get(),
        'due_date': var_due_date.get()
    }

    update_db(db_id, new_value)

    if tree.exists(purchase_id):
        tree.item(purchase_id, values=(
            new_value['product'],
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

    update_status_bar("Record modified with ID: " + str(db_id))
    load_total_accumulated()
    clear_form()
    confirm()


def load_data_into_treeview() -> None:
    """Loads data from the database and populates it into a treeview widget."""
    records = query_db()
    for row in records:
        tree.insert('',
                    'end',
                    text=str(row[0]),
                    values=row[1:])


def get_current_month() -> int:
    """Returns the current month as an integer."""
    return datetime.datetime.now().month


def get_current_month_word(locale_setting=None):
    """Returns the current month's name in the specified locale.
    If no locale is specified, the system's default locale is used."""
    if locale_setting:
        locale.setlocale(locale.LC_TIME, locale_setting)
    else:
        locale.setlocale(locale.LC_TIME, locale.getdefaultlocale())

    current_month = datetime.datetime.now().month
    current_month_str = datetime.datetime.strptime(str(current_month),
                                                   "%m").strftime("%B")
    return current_month_str.capitalize()


def get_total_accumulated() -> float:
    """Calculates and returns the total accumulated value
    for records in the current month."""
    current_month = get_current_month()
    records = query_db(month=current_month)

    total_accumulated = 0
    for row in records:
        total_accumulated += row[0]

    return total_accumulated


def load_total_accumulated() -> float:
    """Loads and returns the total accumulated value for the current month,
    updating a Tkinter variable with this value."""
    total_accumulated = get_total_accumulated()
    var_total.set(f"$ {total_accumulated:.2f}")
    return total_accumulated


def update_total_accumulated_label() -> None:
    """Updates the label to display the total for the current month."""
    current_month_str = get_current_month_word()
    l_total.config(text=f"Total {current_month_str}:")