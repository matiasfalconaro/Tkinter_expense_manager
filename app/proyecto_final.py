import datetime
import locale
import matplotlib.pyplot as plt
import re
import tkinter as tk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from PIL import Image as PilImage, ImageTk

from tkinter import Tk, Frame
from tkinter import *
from tkinter import ttk, messagebox
from tkinter.messagebox import *
from tkcalendar import DateEntry

#  START CONTROLLER

expenses = []  # List to store expenses in memory


def update_status_bar(message): 
    status.config(text=message)
    root.update_idletasks()


def update_due_date_status():
    if var_check_due_date.get():
        e_due_date.config(state='disabled')
    else:
        e_due_date.config(state='normal')


def validate_fields():
    fields_var = [var_product, var_quantity, var_amount, var_supplier, var_date, var_due_date]
    fields_cb = [cb_responsible, cb_category, cb_payment_method]
    
    for var in fields_var:
        if not var.get():
            return False

    for cb in fields_cb:
        if not cb.get():
            return False

    return True


def clear_form():
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


def prepare_add():
    confirm_button.config(state='normal', command=add)
    cancel_button.config(state='normal')


def prepare_delete():
    confirm_button.config(state='normal', command=delete)
    cancel_button.config(state='normal')


def confirm():
    confirm_button.config(state='disabled')
    cancel_button.config(state='disabled')
    for widget in graph_frame.winfo_children():
        widget.destroy()
    create_graph(graph_frame)


def cancel():
    confirm_button.config(state='disabled', command=None)
    cancel_button.config(state='disabled')
    clear_form()


def apply_modification(purchase_id, id_memory):
    if not validate_fields():
        update_status_bar("All fields must be filled.")
        messagebox.showinfo("Info", "All fields must be filled.")
        cancel()
        return

    new_value = {
        'id': id_memory,
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

    for idx, exp in enumerate(expenses):
        if exp['id'] == id_memory:
            expenses[idx] = new_value
            break

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

    update_status_bar("Record modified with ID: " + str(id_memory))
    load_total_accumulated()
    clear_form()
    confirm()


def load_data_into_treeview():
    for row in expenses:
        tree.insert('', 'end', text=str(row['id']), values=list(row.values())[1:])


def get_current_month():
    return datetime.datetime.now().month


def get_current_month_word():
    locale.setlocale(locale.LC_TIME, '')  # Set locale to system default
    current_month = get_current_month()
    current_month_str = datetime.datetime.strptime(str(current_month), "%m").strftime("%B")
    return current_month_str.capitalize()


def get_total_accumulated():
    current_month = get_current_month()
    total_accumulated = 0
    for exp in expenses:
        exp_date = datetime.datetime.strptime(exp['date'], "%Y-%m-%d").month
        if exp_date == current_month:
            total_accumulated += exp['quantity'] * exp['amount']
    return total_accumulated


def load_total_accumulated():
    total_accumulated = get_total_accumulated()
    var_total.set(f"$ {total_accumulated:.2f}")


def update_total_accumulated_label():
    current_month_str = get_current_month_word()
    l_total.config(text=f"Total {current_month_str}:")

#  END CONTROLLER

#  START MODEL

def add():
    var_date.set(cal_date.get_date().strftime("%Y-%m-%d"))
    
    if not var_check_due_date.get():
        due_date_value = e_due_date.get_date().strftime("%Y-%m-%d")
    else:
        due_date_value = 'N/A'
    var_due_date.set(due_date_value)

    if not validate_fields():
        update_status_bar("All input fields must be filled")
        messagebox.showinfo("Info", "All input fields must be filled")
        cancel()
        return

    new_expense = {
        'id': len(expenses) + 1,
        'product': var_product.get(),
        'quantity': int(var_quantity.get()),
        'amount': float(var_amount.get()),
        'responsible': cb_responsible.get(),
        'category': cb_category.get(),
        'supplier': var_supplier.get(),
        'payment_method': cb_payment_method.get(),
        'date': var_date.get(),
        'due_date': due_date_value
    }

    expenses.append(new_expense)

    subtotal_accumulated = round(new_expense['quantity'] * new_expense['amount'], 2)

    tree.insert('',
                'end',
                text=str(new_expense['id']),
                values=(new_expense['product'],
                        new_expense['quantity'],
                        new_expense['amount'],
                        new_expense['responsible'],
                        f"{subtotal_accumulated:.2f}",
                        new_expense['category'],
                        new_expense['supplier'],
                        new_expense['payment_method'],
                        new_expense['date'],
                        new_expense['due_date']))

    load_total_accumulated()
    update_status_bar("Record added with ID: " + str(new_expense['id']))
    clear_form()
    confirm()


def delete():
    purchase_id = tree.focus()
    if not purchase_id:
        messagebox.showinfo("Info", "You must select a record to delete.")
        update_status_bar("You must select a record to delete.")
        cancel()
        return

    id_memory = int(tree.item(purchase_id, 'text'))

    global expenses

    new_expenses = []
    for exp in expenses:
        if exp['id'] != id_memory:
            new_expenses.append(exp)
    expenses = new_expenses
    
    tree.delete(purchase_id)
    load_total_accumulated()
    update_status_bar("Record deleted with ID: " + str(id_memory))
    confirm()


def modify():
    purchase_id = tree.focus()
    if not purchase_id:
        messagebox.showinfo("Info", "You must select a record to modify.")
        update_status_bar("You must select a record to modify.")
        cancel()
        return

    id_memory = int(tree.item(purchase_id, 'text'))

    selected_expense = None
    for exp in expenses:
        if exp['id'] == id_memory:
            selected_expense = exp
            break

    if selected_expense:
        var_product.set(selected_expense['product'])
        var_quantity.set(selected_expense['quantity'])
        var_amount.set(selected_expense['amount'])
        var_date.set(selected_expense['date'])
        cb_responsible.set(selected_expense['responsible'])
        cb_category.set(selected_expense['category'])
        cb_payment_method.set(selected_expense['payment_method'])
        var_supplier.set(selected_expense['supplier'])
        var_due_date.set(selected_expense['due_date'])

    update_status_bar("Modifying record ID: " + str(id_memory))

    confirm_button.config(state='normal', command=lambda: apply_modification(purchase_id, id_memory))
    cancel_button.config(state='normal')


def search():
    search_term = var_search.get()
    if "*" in search_term:
        search_term = ""

    regex = re.compile(search_term, re.IGNORECASE)
    filtered_expenses = []
    for exp in expenses:
        if regex.search(' '.join(map(str, exp.values()))):
            filtered_expenses.append(exp)

    for i in tree.get_children():
        tree.delete(i)

    for exp in filtered_expenses:
        tree.insert('', 'end', text=str(exp['id']), values=list(exp.values())[1:])

    if search_term == "":
        update_status_bar("Showing all records.")
    else:
        update_status_bar(f"Search results for: {search_term}")

    load_total_accumulated()


#  GRAPH (DATA)
def get_graph_data():
    current_month = get_current_month()
    category_totals = {}

    for exp in expenses:
        exp_date = datetime.datetime.strptime(exp['date'], "%Y-%m-%d")
        if exp_date.month == current_month:
            category = exp['category']
            subtotal = exp['quantity'] * exp['amount']  # Calculate subtotal
            if category in category_totals:
                category_totals[category] += subtotal
            else:
                category_totals[category] = subtotal

    graph_data = []
    for category, total in category_totals.items():
        graph_data.append((category, total))
    return graph_data
#  END GRAPH (DATA)
#  END MODEL

##############################################################################

#  START VIEW

root = Tk()
root.grid_rowconfigure(12, weight=1) # Expand the TreeView
root.title('Expense Manager')
root.geometry('1600x900')     # Standard notebook 14' window size

#  FRAMES
header_frame = Frame(root)
header_frame.grid(row=0, column=0, sticky='ew', padx=0, pady=5)

status_frame = Frame(root, borderwidth=1, relief="solid")
status_frame.grid(row=0, column=2, padx=0, pady=10, columnspan=3)

graph_frame = Frame(root, borderwidth=1, relief="solid")
graph_frame.grid(row=2, column=3, rowspan=9, padx=10, pady=0, sticky='nsew')

form_frame = LabelFrame(root, text="Data Entry", padx=10, pady=10)
form_frame.grid(row=2, column=0, columnspan=2, rowspan=6, padx=10,
                      pady=10, sticky="we")

confirmation_frame = Frame(root)
confirmation_frame.grid(row=8, column=0, columnspan=2, padx=10, pady=10)
confirmation_frame.grid_rowconfigure(0, weight=1)
confirmation_frame.grid_columnconfigure(0, weight=1)
confirmation_frame.grid_columnconfigure(1, weight=1)

treeview_frame = Frame(root)
treeview_frame.grid(row=12, column=0, columnspan=11, padx=10, pady=10,
                    sticky='nsew')
treeview_frame.grid_rowconfigure(0, weight=1)
treeview_frame.grid_columnconfigure(0, weight=1)
#  END FRAMES

#  VARIABLES
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
variables_to_validate = [var_product,
                         var_quantity,
                         var_amount,
                         var_responsible,
                         var_supplier,
                         var_payment_method,
                         var_category, var_date, 
                         var_due_date]
# END VARIABLES

# OPTIONS
category_options = ["Maintenance", "Taxes", "Services",
                    "Market", "Cleaning", "School", "Others"]

payment_method_options = ["Cash", "Virtual Wallet",
                          "Cheque", "Credit Card",
                          "Debit Card", "Transfer", "Other"]

responsible_options = ["Gonzalo", "Matías", "Juan"]
# END OPTIONS

#  WIDGETS

#  HEADER
original_image = PilImage.open("app/rsc/tkinter_app_logo.png")
resized_image = original_image.resize((50, 50))
photo = ImageTk.PhotoImage(resized_image)

img = Label(header_frame, image=photo)
img.grid(row=0, column=0, padx=10, pady=5, sticky=W)

title = Label(header_frame, text='EXPENSE MANAGER', font=('Arial', 20, 'bold'))
title.grid(row=0, column=1, padx=0, sticky=W)
#  END HEADER

#  STATUS
status = Label(status_frame, text="Welcome.", font=('Arial', 10),
               width=50, anchor=W)
status.grid(row=0, column=0, sticky=W, padx=0, pady=0)
#  END STATUS

#  FORM
we_width = 30
wcb_width = we_width - 2
l_product = Label(form_frame, text='Product:')
l_product.grid(row=2, column=0, sticky=W)
e_product = Entry(form_frame, textvariable=var_product, width=we_width)
e_product.grid(row=3, column=0, sticky=W, pady=5)

l_quantity = Label(form_frame, text='Quantity:')
l_quantity.grid(row=2, column=1, sticky=W, padx=10)
e_quantity = Entry(form_frame, textvariable=var_quantity, width=we_width)
e_quantity.grid(row=3, column=1, sticky=W, padx=10, pady=5)

l_amount = Label(form_frame, text='Amount:')
l_amount.grid(row=2, column=2, sticky=SW)
e_amount = Entry(form_frame, textvariable=var_amount, width=we_width)
e_amount.grid(row=3, column=2, sticky=W, pady=5)

l_responsible = Label(form_frame, text='Responsible:')
l_responsible.grid(row=4, column=0, sticky=SW)
cb_responsible = ttk.Combobox(form_frame, values=responsible_options,
                              width=wcb_width)
cb_responsible.grid(row=5, column=0, sticky=W, pady=5)

l_category = Label(form_frame, text='Category:')
l_category.grid(row=4, column=1, sticky=SW, padx=10)
cb_category = ttk.Combobox(form_frame, values=category_options, width=wcb_width)
cb_category.grid(row=5, column=1, sticky=W, padx=10, pady=5)

l_supplier = Label(form_frame, text='Supplier:')
l_supplier.grid(row=4, column=2, sticky=SW)
e_supplier = Entry(form_frame, textvariable=var_supplier, width=we_width)
e_supplier.grid(row=5, column=2, sticky=W, pady=5)

l_payment_method = Label(form_frame, text='Payment Method:')
l_payment_method.grid(row=6, column=0, sticky=SW)
cb_payment_method = ttk.Combobox(form_frame, values=payment_method_options,
                             width=wcb_width)
cb_payment_method.grid(row=7, column=0, sticky=W, pady=5)

l_date = Label(form_frame, text='Date:')
l_date.grid(row=6, column=1, sticky=SW, padx=10)
cal_date = DateEntry(form_frame, width=wcb_width, background='darkblue',
                      foreground='white', borderwidth=2)
cal_date.grid(row=7, column=1, sticky=W, padx=10, pady=5)

l_due_date = Label(form_frame, text='Due Date:')
l_due_date.grid(row=6, column=2, sticky=SW)
e_due_date = DateEntry(form_frame, width=wcb_width, background='darkblue',
                          foreground='white', borderwidth=2)
e_due_date.grid(row=7, column=2, sticky=W, pady=5)

l_search = Label(root, text='Search:')
l_search.grid(row=9, column=0, sticky=W, padx=10, pady=5)
e_search = Entry(root, textvariable=var_search, width=12)
e_search.grid(row=10, column=0, sticky='nsew', padx=10, pady=5)

l_total = Label(root, text='Total ', font=('Arial', 10, 'bold'))
l_total.grid(row=8, column=2, sticky=S, pady=5)
e_total = Entry(root, textvariable=var_total, width=20, 
                font=('Arial', 10, 'bold'), justify='center', state='readonly')
e_total.grid(row=9, column=2, sticky=W, padx=10, pady=5)
# END FORM

#  BUTTONS
add_button = tk.Button(root, text='Add', command=prepare_add, bg='grey', fg='white', width=15)
add_button.grid(row=3, column=2, sticky=tk.N)

delete_button = tk.Button(root, text='Delete', command=prepare_delete, bg='grey', fg='white', width=15)
delete_button.grid(row=5, column=2, sticky=tk.N)

modify_button = tk.Button(root, text='Modify', command=modify, bg='grey', fg='white', width=15)
modify_button.grid(row=7, column=2, sticky=tk.N)

search_button = tk.Button(root, text='Search', command=search, bg='grey', fg='white', width=15)
search_button.grid(row=10, column=1, sticky=tk.W)

confirm_button = tk.Button(confirmation_frame, text='Confirm', state='disabled', command=confirm, width=15, bg='green', fg='white')
confirm_button.grid(row=8, column=0, sticky=tk.E)

cancel_button = tk.Button(confirmation_frame, text='Cancel', state='disabled', command=cancel, width=15, bg='red', fg='white')
cancel_button.grid(row=8, column=1, sticky=tk.W)

na_checkbutton = tk.Checkbutton(form_frame, text='N/A', variable=var_check_due_date, command=update_due_date_status)
na_checkbutton.grid(row=6, column=2, sticky=tk.SE, padx=5)

graph_placeholder = tk.Button(graph_frame, bg='white', width=57, pady=118, state='disabled')
graph_placeholder.grid(row=0, column=0, padx=0, pady=0, sticky='e')
#  END BUTTONS

#  GRAPH
def create_graph(graph_frame):
    data = get_graph_data()  # Use the adapted function to get graph data
    current_month_word = get_current_month_word()
    categories = []
    totals = []
   
    for row in data:
        categories.append(row[0][:4])  # Truncate category name to first 4 characters
        totals.append(row[1])

    for category_option in category_options:
        if category_option[:4] not in categories:
            categories.append(category_option[:4])
            totals.append(0)
    
    fig = Figure(figsize=(6, 4), dpi=75)
    plot = fig.add_subplot(1, 1, 1)

    colors = plt.cm.tab20(range(len(categories)))
    
    bars = plot.bar(categories, totals, color=colors)
    
    plot.set_xticks(range(len(categories)))
    plot.set_xticklabels(categories, ha='center', fontsize='small')

    for bar, total in zip(bars, totals):
        yval = bar.get_height()
        plot.text(bar.get_x() + bar.get_width()/2.0, yval, f'${total:.2f}', 
                  va='bottom', ha='center', fontsize='small')

    plot.set_yticks([])
    plot.set_title(f'Total Expenses by Category in {current_month_word}', fontsize=12)
    
    canvas = FigureCanvasTkAgg(fig, master=graph_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True)

graph_placeholder.destroy()
create_graph(graph_frame)
#  END GRAPH

#  TREEVIEW
tree = ttk.Treeview(treeview_frame)
tree.grid(row=0, column=0, sticky='nsew')

tree_scroll_vertical = Scrollbar(treeview_frame, orient="vertical",
                                 command=tree.yview)
tree_scroll_vertical.grid(row=0, column=1, sticky='ns')

tree.configure(yscrollcommand=tree_scroll_vertical.set)

style = ttk.Style(treeview_frame)
style.theme_use("default")
style.configure("Treeview.Heading", 
                 font=('Calibri', 10, 'bold'), 
                 background='black', 
                 foreground='white')

tree['column'] = ('col1', 'col2', 'col3', 'col4', 'col5', 
                  'col6', 'col7', 'col8', 'col9', 'col10')

tree.column('#0', width=50, minwidth=50, stretch=NO) # id
tree.column('col1', width=190, minwidth=50, stretch=NO) # Product
tree.column('col2', width=70, minwidth=50, stretch=NO) # Quantity
tree.column('col3', width=90, minwidth=50, stretch=NO) # Amount
tree.column('col4', width=105, minwidth=50, stretch=NO) # Responsible
tree.column('col5', width=125, minwidth=50, stretch=NO) # Subtotal
tree.column('col6', width=115, minwidth=50, stretch=NO) # Category
tree.column('col7', width=180, minwidth=50, stretch=NO) # Supplier
tree.column('col8', width=120, minwidth=50, stretch=NO) # Payment Method
tree.column('col9', width=90, minwidth=50, stretch=NO) # Date
tree.column('col10', width=100, minwidth=50, stretch=NO) # Due Date

tree.heading('#0', text='Id')
tree.heading('col1', text='Product')
tree.heading('col2', text='Quantity')
tree.heading('col3', text='Amount')
tree.heading('col4', text='Responsible')
tree.heading('col5', text='Subtotal')
tree.heading('col6', text='Category')
tree.heading('col7', text='Supplier')
tree.heading('col8', text='Payment Method')
tree.heading('col9', text='Date')
tree.heading('col10', text='Due Date')
#  END TREEVIEW

#  END WIDGETS

root.mainloop()
#  END VIEW
