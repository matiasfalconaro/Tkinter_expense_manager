import logging
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

from tkcalendar import DateEntry

from .model import Model


class View:
    """Handles UI operations"""
    category_options = []  # Customizable 'Category' dropdown list

    payment_method_options = []  # Customizable 'Payment method' dropdown list

    responsible_options = []  # Customizable 'Responsible' dropdown list

    def __init__(self, controller):
        self.logger = logging.getLogger(__name__)
        
        self.model = Model()
        self.controller = controller
        
        self.root = None
        self.tree = None
        self.status = None
        self.var_amount = None
        self.var_product = None
        self.var_quantity = None
        self.var_date = 0
        self.var_supplier = None
        self.var_responsible = None
        self.var_category = None
        self.cal_date = None
        self.var_payment_method = None
        self.var_total = None
        self.cb_responsible = None
        self.cb_category = None
        self.l_total = None
        self.confirm_button = None
        self.var_due_date = None
        self.graph_frame = None
        self.cancel_button = None
        self.var_search = None
        self.e_due_date = None
        self.var_check_due_date = None
        self.cb_payment_method = None

    def load_total_accumulated(self) -> float:
        """Loads and returns the total accumulated value for the current month,
        updating a Tkinter variable with this value."""
        total_accumulated = self.controller.get_total_accumulated()
        self.var_total.set(f"$ {total_accumulated:.2f}")
        return total_accumulated

    def update_total_accumulated_label(self) -> None:
        """Updates the label to display the total for the current month."""
        current_month_str = self.controller.get_current_month_word()
        self.l_total.config(text=f"Total {current_month_str}:")

    def clear_form(self) -> None:
        """Resets all form fields to their default (empty) values."""
        self.var_amount.set('')
        self.var_product.set('')
        self.var_quantity.set('')
        self.var_supplier.set('')
        self.var_responsible.set('')
        self.var_category.set('')
        self.var_payment_method.set('')
        self.cb_responsible.set('')
        self.cb_category.set('')
        self.cb_payment_method.set('')

    def update_status_bar(self, message: str) -> None:
        """Updates the text of the status bar with the provided message."""
        self.status.config(text=message)
        self.root.update_idletasks()  # Force UI update

    def update_due_date_status(self) -> None:
        """Enables or disables the due date entry
        based on the state of a check variable."""
        state = 'disabled' if self.var_check_due_date.get() else 'normal'
        self.e_due_date.config(state=state)

    def load_data_into_treeview(self) -> None:
        """Loads data from the database
        and populates it into a treeview widget."""
        try:
            records = self.controller.get_query_db()
            for row in records:
                self.tree.insert('',
                                 'end',
                                 text=str(row[0]),
                                 values=row[1:])
        except Exception as e:
            self.logger.error(f"Error loading data into treeview: {e}")

    def create_graph(self, graph_frame: Frame) -> None:
        """Generates and displays a bar graph of monthly expenses
        by category in the specified Tkinter frame."""
        try:
            data = self.controller.get_get_graph_data()
            current_month_word = self.controller.get_current_month_word()

            categories = [row[0][:4] for row in data]
            totals = [row[1] for row in data]

            for category_option in self.category_options:
                if category_option[:4] not in categories:
                    categories.append(category_option[:4])
                    totals.append(0)

            fig = Figure(figsize=(6, 4), dpi=75)
            plot = fig.add_subplot(1, 1, 1)

            colors = plt.colormaps['tab20'](range(len(categories)))
            bar_colors = [colors[i] for i in range(len(categories))]

            bars = plot.bar(categories, totals, color=bar_colors)

            plot.set_xticks(range(len(categories)))
            plot.set_xticklabels(categories, ha='center', fontsize='small')

            for bar, total in zip(bars, totals):
                yval = bar.get_height()
                plot.text(bar.get_x() + bar.get_width()/2.0,
                          yval,
                          f'${total:.2f}',
                          va='bottom',
                          ha='center',
                          fontsize='small')

            plot.set_yticks([])
            plot.set_title(
                f'Total Expenses by Category in {current_month_word}',
                fontsize=12
            )

            canvas = FigureCanvasTkAgg(fig, master=graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)
        except Exception as e:
            self.logger.error(f"Error creating graph: {e}")

    def create_view(self):
        self.root = Tk()
        self.root.grid_columnconfigure(0,
                                       weight=1)
        self.root.grid_columnconfigure(1,
                                       weight=0)
        self.root.grid_columnconfigure(2,
                                       weight=1)
        self.root.grid_columnconfigure(3,
                                       weight=1)
        self.root.grid_rowconfigure(12,
                                    weight=1)  # Expand the TreeView

        self.root.title('Expense Manager')
        self.root.geometry('1600x900')  # Standard window size for 14' notebook

        # FRAMES
        header_frame = Frame(self.root)
        header_frame.grid(row=0,
                          column=0,
                          sticky='ew',
                          padx=0,
                          pady=5)
        header_frame.grid_columnconfigure(1,
                                          weight=1)

        version_frame = Frame(self.root,
                              borderwidth=1,
                              relief="solid")
        version_frame.grid(row=0,
                           column=1,
                           sticky='ew',
                           padx=20,
                           pady=10)
        version_frame.grid_columnconfigure(0,
                                           weight=1)
        version_frame.grid_columnconfigure(1,
                                           weight=0)
        version_frame.grid_columnconfigure(2,
                                           weight=1)

        status_frame = Frame(self.root,
                             borderwidth=1,
                             relief="solid")
        status_frame.grid(row=0,
                          column=3,
                          sticky='ew',
                          padx=10,
                          pady=0,
                          columnspan=3)

        self.graph_frame = Frame(self.root,
                                 borderwidth=1,
                                 relief="solid")
        self.graph_frame.grid(row=2,
                              column=3,
                              rowspan=9,
                              padx=10,
                              pady=0,
                              sticky='nsew')

        data_entry_frame = LabelFrame(self.root,
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

        confirmation_frame = Frame(self.root)
        confirmation_frame.grid(row=8,
                                column=0,
                                columnspan=2,
                                padx=10,
                                pady=10)
        confirmation_frame.grid_rowconfigure(0,
                                             weight=1)
        confirmation_frame.grid_columnconfigure(0,
                                                weight=1)
        confirmation_frame.grid_columnconfigure(1,
                                                weight=1)

        treeview_frame = Frame(self.root)
        treeview_frame.grid(row=12,
                            column=0,
                            columnspan=11,
                            padx=10,
                            pady=10,
                            sticky='nsew')
        treeview_frame.grid_rowconfigure(0,
                                         weight=1)
        treeview_frame.grid_columnconfigure(0,
                                            weight=1)
        # END FRAMES

        self.var_id = IntVar()
        self.var_product = StringVar()
        self.var_quantity = IntVar()
        self.var_amount = StringVar()
        self.var_responsible = StringVar()
        self.var_subtotal = StringVar()
        self.var_total = StringVar()
        self.var_category = StringVar()
        self.var_supplier = StringVar()
        self.var_payment_method = StringVar()
        self.var_date = StringVar()
        self.var_due_date = StringVar()
        self.var_check_due_date = BooleanVar()
        self.var_search = StringVar()

        self.fields_to_validate = [self.var_product,
                                   self.var_quantity,
                                   self.var_amount,
                                   self.var_responsible,
                                   self.var_supplier,
                                   self.var_payment_method,
                                   self.var_category,
                                   self.var_date,
                                   self.var_due_date]

        # WIDGETS

        # HEADER
        original_image = PilImage.open("app/rsc/tkinter_app_logo.png")
        resized_image = original_image.resize((50, 50))
        photo = ImageTk.PhotoImage(resized_image)

        img = Label(header_frame,
                    image=photo)
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
        self.status = Label(status_frame,
                            text="Welcome.",
                            font=('Arial', 10),
                            width=50,
                            anchor=W)
        self.status.grid(row=0,
                         column=3,
                         sticky=W,
                         padx=0,
                         pady=0)
        # END STATUS

        # VERSION
        version = Label(version_frame,
                        text="Version 1.1.0",
                        font=('Arial', 10, 'bold'),
                        bg='grey',
                        fg='white')
        version.grid(row=0,
                     column=1,
                     sticky='ew')

        # END VERSION

        # FORM
        entry_width = 30
        combo_width = entry_width - 2
        self.l_product = Label(data_entry_frame,
                               text='Product:')
        self.l_product.grid(row=2,
                            column=0,
                            sticky=W)
        self.e_product = Entry(data_entry_frame,
                               textvariable=self.var_product,
                               width=entry_width)
        self.e_product.grid(row=3,
                            column=0,
                            sticky=W,
                            pady=5)

        self.l_quantity = Label(data_entry_frame,
                                text='Quantity:')
        self.l_quantity.grid(row=2,
                             column=1,
                             sticky=W,
                             padx=10)
        self.e_quantity = Entry(data_entry_frame,
                                textvariable=self.var_quantity,
                                width=entry_width)
        self.e_quantity.grid(row=3,
                             column=1,
                             sticky=W,
                             padx=10,
                             pady=5)

        self.l_amount = Label(data_entry_frame,
                              text='Amount:')
        self.l_amount.grid(row=2,
                           column=2,
                           sticky=SW)
        self.e_amount = Entry(data_entry_frame,
                              textvariable=self.var_amount,
                              width=entry_width)
        self.e_amount.grid(row=3,
                           column=2,
                           sticky=W,
                           pady=5)

        self.l_responsible = Label(data_entry_frame,
                                   text='Responsible:')
        self.l_responsible.grid(row=4,
                                column=0,
                                sticky=SW)
        self.cb_responsible = ttk.Combobox(data_entry_frame,
                                           values=self.responsible_options,
                                           width=combo_width)
        self.cb_responsible.grid(row=5,
                                 column=0,
                                 sticky=W,
                                 pady=5)

        self.l_category = Label(data_entry_frame,
                                text='Category:')
        self.l_category.grid(row=4,
                             column=1,
                             sticky=SW,
                             padx=10)
        self.cb_category = ttk.Combobox(data_entry_frame,
                                        values=self.category_options,
                                        width=combo_width)
        self.cb_category.grid(row=5,
                              column=1,
                              sticky=W,
                              padx=10,
                              pady=5)

        self.l_supplier = Label(data_entry_frame,
                                text='Supplier:')
        self.l_supplier.grid(row=4,
                             column=2,
                             sticky=SW)
        self.e_supplier = Entry(data_entry_frame,
                                textvariable=self.var_supplier,
                                width=entry_width)
        self.e_supplier.grid(row=5,
                             column=2,
                             sticky=W,
                             pady=5)
        self.l_payment_method = Label(data_entry_frame,
                                      text='Payment Method:')
        self.l_payment_method.grid(row=6,
                                   column=0,
                                   sticky=SW)
        self.cb_payment_method = ttk.Combobox(
                                        data_entry_frame,
                                        values=self.payment_method_options,
                                        width=combo_width)
        self.cb_payment_method.grid(row=7,
                                    column=0,
                                    sticky=W,
                                    pady=5)

        self.l_date = Label(data_entry_frame,
                            text='Date:')
        self.l_date.grid(row=6,
                         column=1,
                         sticky=SW,
                         padx=10)
        self.cal_date = DateEntry(data_entry_frame,
                                  width=combo_width,
                                  background='darkblue',
                                  foreground='white',
                                  borderwidth=2)
        self.cal_date.grid(row=7,
                           column=1,
                           sticky=W,
                           padx=10,
                           pady=5)

        self.l_due_date = Label(data_entry_frame,
                                text='Due Date:')
        self.l_due_date.grid(row=6,
                             column=2,
                             sticky=SW)
        self.e_due_date = DateEntry(data_entry_frame,
                                    width=combo_width,
                                    background='darkblue',
                                    foreground='white',
                                    borderwidth=2)
        self.e_due_date.grid(row=7,
                             column=2,
                             sticky=W,
                             pady=5)

        self.l_search = Label(self.root,
                              text='Search:')
        self.l_search.grid(row=9,
                           column=0,
                           sticky=W,
                           padx=10,
                           pady=5)
        self.e_search = Entry(self.root,
                              textvariable=self.var_search,
                              width=12)
        self.e_search.grid(row=10,
                           column=0,
                           sticky='nsew',
                           padx=10,
                           pady=5)

        self.l_total = Label(self.root,
                             text='Total ',
                             font=('Arial',
                                   10,
                                   'bold'))
        self.l_total.grid(row=8,
                          column=2,
                          sticky=S,
                          pady=5)
        self.e_total = Entry(self.root,
                             textvariable=self.var_total,
                             width=20,
                             font=('Arial',
                                   10,
                                   'bold'),
                             justify='center',
                             state='readonly')
        self.e_total.grid(row=9,
                          column=2,
                          sticky=W,
                          padx=10,
                          pady=5)
        # END FORM

        # BUTTONS
        self.add_button = Button(self.root,
                                 text='Add',
                                 command=self.controller.prepare_add,
                                 bg='grey',
                                 fg='white',
                                 width=15)
        self.add_button.grid(row=3,
                             column=2,
                             sticky=N)

        self.delete_button = Button(self.root,
                                    text='Delete',
                                    command=self.controller.prepare_delete,
                                    bg='grey',
                                    fg='white',
                                    width=15)
        self.delete_button.grid(row=5,
                                column=2,
                                sticky=N)

        self.modify_button = Button(self.root,
                                    text='Modify',
                                    command=self.controller.modify,
                                    bg='grey',
                                    fg='white',
                                    width=15)
        self.modify_button.grid(row=7,
                                column=2,
                                sticky=N)

        self.search_button = Button(self.root,
                                    text='Search',
                                    command=self.controller.search,
                                    bg='grey',
                                    fg='white',
                                    width=15)
        self.search_button.grid(row=10,
                                column=1,
                                sticky=W)

        self.confirm_button = Button(confirmation_frame,
                                     text='Confirm',
                                     state='disabled',
                                     command=self.controller.confirm,
                                     width=15,
                                     bg='green',
                                     fg='white')
        self.confirm_button.grid(row=8,
                                 column=0,
                                 sticky=E)

        self.cancel_button = Button(confirmation_frame,
                                    text='Cancel',
                                    state='disabled',
                                    command=self.controller.cancel,
                                    width=15,
                                    bg='red',
                                    fg='white')
        self.cancel_button.grid(row=8,
                                column=1,
                                sticky=W)

        self.na_checkbutton = Checkbutton(data_entry_frame,
                                          text='N/A',
                                          variable=self.var_check_due_date,
                                          command=self.update_due_date_status)
        self.na_checkbutton.grid(row=6,
                                 column=2,
                                 sticky=SE,
                                 padx=5)

        self.graph_placeholder = Button(self.graph_frame,
                                        bg='white',
                                        width=57,
                                        pady=118,
                                        state='disabled')
        self.graph_placeholder.grid(row=0,
                                    column=0,
                                    padx=0,
                                    pady=0,
                                    sticky='e')
        # END BUTTONS

        # TREEVIEW
        self.tree = ttk.Treeview(treeview_frame)
        self.tree.grid(row=0,
                       column=0,
                       sticky='nsew')

        tree_scroll_vertical = Scrollbar(treeview_frame,
                                         orient="vertical",
                                         command=self.tree.yview)
        tree_scroll_vertical.grid(row=0,
                                  column=1,
                                  sticky='ns')

        self.tree.configure(yscrollcommand=tree_scroll_vertical.set)

        style = ttk.Style(treeview_frame)
        style.theme_use("default")
        style.configure("Treeview.Heading",
                        font=('Calibri', 10, 'bold'),
                        background='black',
                        foreground='white')

        self.tree['column'] = ('col1',
                               'col2',
                               'col3',
                               'col4',
                               'col5',
                               'col6',
                               'col7',
                               'col8',
                               'col9',
                               'col10')
        self.tree.column('#0',
                         width=50,
                         minwidth=50,
                         stretch=NO)  # id
        self.tree.column('col1',
                         width=190,
                         minwidth=50,
                         stretch=NO)  # Product
        self.tree.column('col2',
                         width=70,
                         minwidth=50,
                         stretch=NO)  # Quantity
        self.tree.column('col3',
                         width=90,
                         minwidth=50,
                         stretch=NO)  # Amount
        self.tree.column('col4',
                         width=105,
                         minwidth=50,
                         stretch=NO)  # Responsible
        self.tree.column('col5',
                         width=125,
                         minwidth=50,
                         stretch=NO)  # Subtotal
        self.tree.column('col6',
                         width=115,
                         minwidth=50,
                         stretch=NO)  # Category
        self.tree.column('col7',
                         width=190,
                         minwidth=50,
                         stretch=NO)  # Supplier
        self.tree.column('col8',
                         width=200,
                         minwidth=50,
                         stretch=NO)  # Payment Method
        self.tree.column('col9',
                         width=90,
                         minwidth=50,
                         stretch=NO)  # Date
        self.tree.column('col10',
                         width=100,
                         minwidth=50,
                         stretch=NO)  # Due Date

        self.tree.heading('#0',
                          text='Id')
        self.tree.heading('col1',
                          text='Product')
        self.tree.heading('col2',
                          text='Quantity')
        self.tree.heading('col3',
                          text='Amount')
        self.tree.heading('col4',
                          text='Responsible')
        self.tree.heading('col5',
                          text='Subtotal')
        self.tree.heading('col6',
                          text='Category')
        self.tree.heading('col7',
                          text='Supplier')
        self.tree.heading('col8',
                          text='Payment Method')
        self.tree.heading('col9',
                          text='Date')
        self.tree.heading('col10',
                          text='Due Date')
        # END TREEVIEW

        # END WIDGETS
        self.graph_placeholder.destroy()
        self.create_graph(self.graph_frame)
        self.update_total_accumulated_label()
        self.load_total_accumulated()
        self.load_data_into_treeview()
        self.root.mainloop()
