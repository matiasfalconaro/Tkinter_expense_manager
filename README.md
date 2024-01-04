# Expense Manager

## Description
Expense Manager is a Python and Tkinter-based application tailored for management of personal or business expenses. Utilizing SQLite3 for data persistence, it offers a solution for expense tracking and visualization.

## Steps to Start Collaborating
- Assign yourself an issue.
- Relate the issue with the next available branch number.
- Create a branch from main, named `nextbranchNr_branch_name`.
- Push changes to that branch. Once the functionality is completed, tag it as ready-for-review.
- The reviewer will indicate whether changes need to be made (by removing the tag) or not.
- Once the changes are finalized, the reviewer will merge into the main branch.

IMPORTANT: Do NOT commit to the main branch.

## Key Features
- **SQLite3 Database Integration:** Data storage and retrieval for expense records.
- **Python & Tkinter Interface:** Interface built with Python's Tkinter.
- **MVC Design Pattern:** Organized code structure using the Model-View-Controller paradigm.
- **Graphical Data Visualization:** Matplotlib integration to graphically represent expenses.
- **Data Validation:** Ensures the integrity and accuracy of input data.
- **CRUD Operations:** Full Create, Read, Update, Delete functionalities for expense management.

### Prerequisites
- Python 3.x
- Virtual environment tool

### Setup
1. Install Dependencies:
   pip install -r requirements.txt

2. Run the Application:
   python app/main.py

## Usage
- **Add Expense Records:** Capture expense details through an intuitive form.
- **Manage Expenses:** Perform CRUD operations on expense data.
- **Search and Filter:** Quickly find specific expense records.
- **Visualize Data:** Monthly expenses visualized in bar graphs.
- **SQLite3 Data Storage:** Reliable data management with SQLite3.

## Data Model

| Column            | Data Type | Properties                  |
|-------------------|-----------|-----------------------------|
| id                | INTEGER   | PRIMARY KEY, AUTOINCREMENT  |
| product_service   | TEXT      |                             |
| quantity          | INTEGER   |                             |
| amount            | FLOAT     |                             |
| responsible       | TEXT      |                             |
| subtotal          | FLOAT     |                             |
| category          | TEXT      |                             |
| supplier          | TEXT      |                             |
| payment_method    | TEXT      |                             |
| date              | DATE      |                             |
| due_date          | DATE      |                             |

## About the project
'Expense Manager' is developed for educational purposes, demonstrating Python and Tkinter's capabilities in desktop application development.
