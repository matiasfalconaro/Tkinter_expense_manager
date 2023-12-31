import datetime
import locale
import re
import sqlite3

import matplotlib.pyplot as plt

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from PIL import Image as PilImage, ImageTk

from tkinter import Tk
from tkinter import (BooleanVar,
                     Button,
                     Checkbutton,
                     Entry,
                     Frame,
                     IntVar,
                     Label,
                     LabelFrame)
from tkinter import (N,
                     E,
                     S,
                     W,
                     NO,
                     SE,
                     SW)
from tkinter import (Scrollbar,
                     StringVar)
from tkinter import ttk
from tkinter.messagebox import showinfo

from tkcalendar import DateEntry

from typing import Optional, List, Tuple


# START CONTROLLER
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
# END CONTROLLER

##############################################################################

# START MODEL


# CRUD
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
    current_month_num = str(get_current_month())
    query = f"""SELECT category, SUM(subtotal)
                FROM expenses
                WHERE strftime('%m', date) = '{current_month_num}'
                GROUP BY category"""
    cursor.execute(query)
    data = cursor.fetchall()
    disconnect_from_database(conn)
    return data
# END GRAPH (DATA)

# END MODEL

##############################################################################


# START VIEW
root = Tk()
root.grid_columnconfigure(0,
                          weight=1)
root.grid_columnconfigure(1,
                          weight=0)  # The column that contains the version_frame
root.grid_columnconfigure(2,
                          weight=1)
root.grid_columnconfigure(3,
                          weight=1)
root.grid_rowconfigure(12,
                       weight=1)  # Expand the TreeView

root.title('Expense Manager')
root.geometry('1600x900')  # Standard window size for 14' notebook

# FRAMES
header_frame = Frame(root)
header_frame.grid(row=0,
                  column=0,
                  sticky='ew',
                  padx=0,
                  pady=5)
header_frame.grid_columnconfigure(1,
                                  weight=1)

version_frame = Frame(root,
                      borderwidth=1,
                      relief="solid")
version_frame.grid(row=0,
                   column=1,  # Adjust the column index as necessary
                   sticky='ew',  # The frame will expand to fill the width of the column
                   padx=20,  # Increase padding to reduce the width of the actual content area
                   pady=10)
version_frame.grid_columnconfigure(0, weight=1)
version_frame.grid_columnconfigure(1, weight=0)  # Actual column for the version label
version_frame.grid_columnconfigure(2, weight=1)

status_frame = Frame(root,
                     borderwidth=1,
                     relief="solid")
status_frame.grid(row=0,
                  column=3,
                  sticky='ew',
                  padx=10,
                  pady=0,
                  columnspan=3)

graph_frame = Frame(root,
                    borderwidth=1,
                    relief="solid")
graph_frame.grid(row=2,
                 column=3,
                 rowspan=9,
                 padx=10,
                 pady=0,
                 sticky='nsew')

data_entry_frame = LabelFrame(root,
                              text="Data Entry",
                              padx=10,
                              pady=10)
data_entry_frame.grid(row=2,
                      column=0,
                      columnspan=2,
                      rowspan=6,
                      padx=10,
                      pady=10,
                      sticky="we")

confirmation_frame = Frame(root)
confirmation_frame.grid(row=8,
                        column=0,
                        columnspan=2,
                        padx=10,
                        pady=10)
confirmation_frame.grid_rowconfigure(0, weight=1)
confirmation_frame.grid_columnconfigure(0, weight=1)
confirmation_frame.grid_columnconfigure(1, weight=1)

treeview_frame = Frame(root)
treeview_frame.grid(row=12,
                    column=0,
                    columnspan=11,
                    padx=10,
                    pady=10,
                    sticky='nsew')
treeview_frame.grid_rowconfigure(0, weight=1)
treeview_frame.grid_columnconfigure(0, weight=1)
# END FRAMES

var_id = IntVar()
var_product = StringVar()
var_quantity = IntVar()
var_amount = StringVar()
var_responsible = StringVar()
var_subtotal = StringVar()
var_total = StringVar()
var_category = StringVar()
var_supplier = StringVar()
var_payment_method = StringVar()
var_date = StringVar()
var_due_date = StringVar()
var_check_due_date = BooleanVar()
var_search = StringVar()

fields_to_validate = [var_product,
                      var_quantity,
                      var_amount,
                      var_responsible,
                      var_supplier,
                      var_payment_method,
                      var_category, var_date,
                      var_due_date]

category_options = ["Maintenance",
                    "Taxes",
                    "Services",
                    "Market",
                    "Cleaning",
                    "School",
                    "Others"]

payment_method_options = ["Cash",
                          "Virtual Wallet",
                          "Check",
                          "Credit Card",
                          "Debit Card",
                          "Transfer",
                          "Other"]

responsible_options = ["Matías",
                       "Gonzalo",
                       "Juan"]

# WIDGETS

# HEADER
original_image = PilImage.open("app/rsc/tkinter_app_logo.png")
resized_image = original_image.resize((50, 50))
photo = ImageTk.PhotoImage(resized_image)

img = Label(header_frame, image=photo)
img.grid(row=0,
         column=0,
         padx=10,
         pady=5,
         sticky=W)

title = Label(header_frame,
              text='EXPENSE MANAGER',
              font=('Arial',
                    20,
                    'bold'))
title.grid(row=0,
           column=1,
           padx=0,
           sticky=W)
# END HEADER

# STATUS
status = Label(status_frame,
               text="Welcome.",
               font=('Arial', 10),
               width=50,
               anchor=W)
status.grid(row=0,
            column=3,
            sticky=W,
            padx=0,
            pady=0)
# END STATUS

# VERSION
version = Label(version_frame,
                text="Version 1.0.0",
                font=('Arial', 10, 'bold'),
                bg='grey',
                fg='white')
version.grid(row=0,
             column=1,
             sticky='ew')  # Center the label in the frame

# END VERSION

# FORM
entry_width = 30
combo_width = entry_width - 2
l_product = Label(data_entry_frame,
                  text='Product:')
l_product.grid(row=2,
               column=0,
               sticky=W)
e_product = Entry(data_entry_frame,
                  textvariable=var_product,
                  width=entry_width)
e_product.grid(row=3,
               column=0,
               sticky=W,
               pady=5)

l_quantity = Label(data_entry_frame,
                   text='Quantity:')
l_quantity.grid(row=2,
                column=1,
                sticky=W,
                padx=10)
e_quantity = Entry(data_entry_frame,
                   textvariable=var_quantity,
                   width=entry_width)
e_quantity.grid(row=3,
                column=1,
                sticky=W,
                padx=10,
                pady=5)

l_amount = Label(data_entry_frame,
                 text='Amount:')
l_amount.grid(row=2,
              column=2,
              sticky=SW)
e_amount = Entry(data_entry_frame,
                 textvariable=var_amount,
                 width=entry_width)
e_amount.grid(row=3,
              column=2,
              sticky=W,
              pady=5)

l_responsible = Label(data_entry_frame,
                      text='Responsible:')
l_responsible.grid(row=4,
                   column=0,
                   sticky=SW)
cb_responsible = ttk.Combobox(data_entry_frame,
                              values=responsible_options,
                              width=combo_width)
cb_responsible.grid(row=5,
                    column=0,
                    sticky=W,
                    pady=5)

l_category = Label(data_entry_frame,
                   text='Category:')
l_category.grid(row=4,
                column=1,
                sticky=SW,
                padx=10)
cb_category = ttk.Combobox(data_entry_frame,
                           values=category_options,
                           width=combo_width)
cb_category.grid(row=5,
                 column=1,
                 sticky=W,
                 padx=10,
                 pady=5)

l_supplier = Label(data_entry_frame,
                   text='Supplier:')
l_supplier.grid(row=4,
                column=2,
                sticky=SW)
e_supplier = Entry(data_entry_frame,
                   textvariable=var_supplier,
                   width=entry_width)
e_supplier.grid(row=5,
                column=2,
                sticky=W,
                pady=5)

l_payment_method = Label(data_entry_frame,
                         text='Payment Method:')
l_payment_method.grid(row=6,
                      column=0,
                      sticky=SW)
cb_payment_method = ttk.Combobox(data_entry_frame,
                                 values=payment_method_options,
                                 width=combo_width)
cb_payment_method.grid(row=7,
                       column=0,
                       sticky=W,
                       pady=5)

l_date = Label(data_entry_frame,
               text='Date:')
l_date.grid(row=6,
            column=1,
            sticky=SW,
            padx=10)
cal_date = DateEntry(data_entry_frame,
                     width=combo_width,
                     background='darkblue',
                     foreground='white',
                     borderwidth=2)
cal_date.grid(row=7,
              column=1,
              sticky=W,
              padx=10,
              pady=5)

l_due_date = Label(data_entry_frame,
                   text='Due Date:')
l_due_date.grid(row=6,
                column=2,
                sticky=SW)
e_due_date = DateEntry(data_entry_frame,
                       width=combo_width,
                       background='darkblue',
                       foreground='white',
                       borderwidth=2)
e_due_date.grid(row=7,
                column=2,
                sticky=W,
                pady=5)

l_search = Label(root,
                 text='Search:')
l_search.grid(row=9,
              column=0,
              sticky=W,
              padx=10,
              pady=5)
e_search = Entry(root,
                 textvariable=var_search,
                 width=12)
e_search.grid(row=10,
              column=0,
              sticky='nsew',
              padx=10,
              pady=5)

l_total = Label(root,
                text='Total ',
                font=('Arial',
                      10,
                      'bold'))
l_total.grid(row=8,
             column=2,
             sticky=S,
             pady=5)
e_total = Entry(root,
                textvariable=var_total,
                width=20,
                font=('Arial',
                      10,
                      'bold'),
                justify='center',
                state='readonly')
e_total.grid(row=9,
             column=2,
             sticky=W,
             padx=10,
             pady=5)
# END FORM

# BUTTONS
add_button = Button(root,
                    text='Add',
                    command=prepare_add,
                    bg='grey',
                    fg='white',
                    width=15)
add_button.grid(row=3,
                column=2,
                sticky=N)

delete_button = Button(root,
                       text='Delete',
                       command=prepare_delete,
                       bg='grey',
                       fg='white',
                       width=15)
delete_button.grid(row=5,
                   column=2,
                   sticky=N)

modify_button = Button(root,
                       text='Modify',
                       command=modify,
                       bg='grey',
                       fg='white',
                       width=15)
modify_button.grid(row=7,
                   column=2,
                   sticky=N)

search_button = Button(root,
                       text='Search',
                       command=search,
                       bg='grey',
                       fg='white',
                       width=15)
search_button.grid(row=10,
                   column=1,
                   sticky=W)

confirm_button = Button(confirmation_frame,
                        text='Confirm',
                        state='disabled',
                        command=confirm,
                        width=15,
                        bg='green',
                        fg='white')
confirm_button.grid(row=8,
                    column=0,
                    sticky=E)

cancel_button = Button(confirmation_frame,
                       text='Cancel',
                       state='disabled',
                       command=cancel,
                       width=15,
                       bg='red',
                       fg='white')
cancel_button.grid(row=8,
                   column=1,
                   sticky=W)

na_checkbutton = Checkbutton(data_entry_frame,
                             text='N/A',
                             variable=var_check_due_date,
                             command=update_due_date_status)
na_checkbutton.grid(row=6,
                    column=2,
                    sticky=SE,
                    padx=5)

graph_placeholder = Button(graph_frame,
                           bg='white',
                           width=57,
                           pady=118,
                           state='disabled')
graph_placeholder.grid(row=0,
                       column=0,
                       padx=0,
                       pady=0,
                       sticky='e')
# END BUTTONS

# TREEVIEW
tree = ttk.Treeview(treeview_frame)
tree.grid(row=0,
          column=0,
          sticky='nsew')

tree_scroll_vertical = Scrollbar(treeview_frame,
                                 orient="vertical",
                                 command=tree.yview)
tree_scroll_vertical.grid(row=0,
                          column=1,
                          sticky='ns')

tree.configure(yscrollcommand=tree_scroll_vertical.set)

style = ttk.Style(treeview_frame)
style.theme_use("default")
style.configure("Treeview.Heading",
                font=('Calibri', 10, 'bold'),
                background='black',
                foreground='white')

tree['column'] = ('col1',
                  'col2',
                  'col3',
                  'col4',
                  'col5',
                  'col6',
                  'col7',
                  'col8',
                  'col9',
                  'col10')

tree.column('#0',
            width=50,
            minwidth=50,
            stretch=NO)  # id
tree.column('col1',
            width=190,
            minwidth=50,
            stretch=NO)  # Product
tree.column('col2',
            width=70,
            minwidth=50,
            stretch=NO)  # Quantity
tree.column('col3',
            width=90,
            minwidth=50,
            stretch=NO)  # Amount
tree.column('col4',
            width=105,
            minwidth=50,
            stretch=NO)  # Responsible
tree.column('col5',
            width=125,
            minwidth=50,
            stretch=NO)  # Subtotal
tree.column('col6',
            width=115,
            minwidth=50,
            stretch=NO)  # Category
tree.column('col7',
            width=180,
            minwidth=50,
            stretch=NO)  # Supplier
tree.column('col8',
            width=200,
            minwidth=50,
            stretch=NO)  # Payment Method
tree.column('col9',
            width=90,
            minwidth=50,
            stretch=NO)  # Date
tree.column('col10',
            width=100,
            minwidth=50,
            stretch=NO)  # Due Date

tree.heading('#0',
             text='Id')
tree.heading('col1',
             text='Product')
tree.heading('col2',
             text='Quantity')
tree.heading('col3',
             text='Amount')
tree.heading('col4',
             text='Responsible')
tree.heading('col5',
             text='Subtotal')
tree.heading('col6',
             text='Category')
tree.heading('col7',
             text='Supplier')
tree.heading('col8',
             text='Payment Method')
tree.heading('col9',
             text='Date')
tree.heading('col10',
             text='Due Date')
# END TREEVIEW


# GRAPH
def create_graph(graph_frame: Frame) -> None:
    """Generates and displays a bar graph of monthly expenses
    by category in the specified Tkinter frame."""
    data = get_graph_data()
    current_month_word = get_current_month_word()
    categories = []
    totals = []

    for row in data:
        categories.append(row[0][:4])
        totals.append(row[1])

    for category_option in category_options:
        if category_option[:4] not in categories:
            categories.append(category_option[:4])
            totals.append(0)

    fig = Figure(figsize=(6, 4), dpi=75)
    plot = fig.add_subplot(1, 1, 1)

    colors = plt.colormaps['tab20'](range(len(categories)))

    bar_colors = []
    for i in range(len(categories)):
        bar_colors.append(colors[i])

    bars = plot.bar(categories,
                    totals,
                    color=bar_colors)

    plot.set_xticks(range(len(categories)))
    plot.set_xticklabels(categories,
                         ha='center',
                         fontsize='small')

    for bar, total in zip(bars, totals):
        yval = bar.get_height()
        plot.text(bar.get_x() + bar.get_width()/2.0,
                  yval,
                  f'${total:.2f}',
                  va='bottom',
                  ha='center',
                  fontsize='small')

    plot.set_yticks([])
    plot.set_title(f'Total Expenses by Category in {current_month_word}',
                   fontsize=12)

    canvas = FigureCanvasTkAgg(fig,
                               master=graph_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both',
                                expand=True)


graph_placeholder.destroy()
create_graph(graph_frame)
# END GRAPH

# END WIDGETS

update_total_accumulated_label()
load_total_accumulated()
load_data_into_treeview()
root.mainloop()
# END VIEW
