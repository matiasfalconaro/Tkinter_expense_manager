import tkinter as tk

from PIL import Image as PilImage, ImageTk

from tkinter import Tk, Frame
from tkinter import *
from tkinter import ttk
from tkinter.messagebox import *
from tkcalendar import DateEntry

#------------------------------START CONTROLLER------------------------------#

def do_nothing():
    pass

#-------------------------------END CONTROLLER-------------------------------#

##############################################################################

#--------------------------------START MODEL---------------------------------#

#----------------------------------END MODEL---------------------------------#

##############################################################################

#--------------------------------START VIEW----------------------------------#

root = Tk()
root.grid_rowconfigure(12, weight=1) # Expand the TreeView
root.title('Expense Manager')
root.geometry('1600x900')     # Standard notebook 14' window size

#-----FRAMES-----#
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
#-----END FRAMES-----#

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

category_options = ["Maintenance", "Taxes", "Services",
                    "Market", "Cleaning", "School", "Others"]

payment_method_options = ["Cash", "Virtual Wallet",
                          "Cheque", "Credit Card",
                          "Debit Card", "Transfer", "Other"]

responsible_options = ["Gonzalo", "Matías", "Juan"]

#-----WIDGETS-----#

#-----HEADER-----#
original_image = PilImage.open("app/rsc/tkinter_app_logo.png")
resized_image = original_image.resize((50, 50))
photo = ImageTk.PhotoImage(resized_image)

img = Label(header_frame, image=photo)
img.grid(row=0, column=0, padx=10, pady=5, sticky=W)

title = Label(header_frame, text='EXPENSE MANAGER', font=('Arial', 20, 'bold'))
title.grid(row=0, column=1, padx=0, sticky=W)
#-----END HEADER-----#

#-----STATUS-----#
status = Label(status_frame, text="Welcome.", font=('Arial', 10),
               width=50, anchor=W)
status.grid(row=0, column=0, sticky=W, padx=0, pady=0)
#-----END STATUS-----#

#-----FORM-----#
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
#-----END FORM-----#

#-----BUTTONS-----#
add_button = Button(root, text='Add', command=do_nothing, bg='grey', fg='white', width=15)
add_button.grid(row=3, column=2, sticky=N)

delete_button = Button(root, text='Delete', command=do_nothing, bg='grey', fg='white', width=15)
delete_button.grid(row=5, column=2, sticky=N)

modify_button = Button(root, text='Modify',
                            command=do_nothing, bg='grey', fg='white', width=15)
modify_button.grid(row=7, column=2, sticky=N)

search_button = Button(root, text='Search', command=do_nothing, bg='grey', fg='white', width=15)
search_button.grid(row=10, column=1, sticky=W)

confirm_button = Button(confirmation_frame, text='Confirm', state='disabled', command=do_nothing, width=15,
                         bg='green', fg='white')
confirm_button.grid(row=8, column=0, sticky=E)

cancel_button = Button(confirmation_frame, text='Cancel', state='disabled', command=do_nothing, width=15,
                        bg='red', fg='white')
cancel_button.grid(row=8, column=1, sticky=W)

na_checkbutton = Checkbutton(form_frame, text='N/A',
                             variable=var_check_due_date,
                             command=do_nothing)
na_checkbutton.grid(row=6, column=2, sticky=SE, padx=5)

graph_placeholder = Button(graph_frame, bg='white',
                     width=57, pady=118, state='disabled')
graph_placeholder.grid(row=0, column=0, padx=0, pady=0, sticky='e')
#-----END BUTTONS-----#

#-----TREEVIEW-----#
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
#-----END TREEVIEW-----#

#-----END WIDGETS-----#

root.mainloop()
#---------------------------------END VIEW----------------------------------#
