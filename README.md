# Expense Manager

## Description
Expense Manager is a Python and Tkinter-based application tailored for management of personal or business expenses. Utilizing SQLite3 for data persistence, it offers a solution for expense tracking and visualization.

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

### Setup and Virtual Environment
1. Clone the Repository:
   git clone https://github.com/your-github-username/tkinter_expense_manager.git

2. Navigate to the Project Directory:
   cd tkinter_expense_manager

3. Create and Activate a Virtual Environment:
   - On Windows:
     python -m venv expense_manager
     .\expense_manager\Scripts\activate

   - On Unix or MacOS:
     python3 -m venv expense_manager
     source expense_manager/bin/activate

4. Install Dependencies:
   pip install -r requirements.txt

5. Run the Application:
   python app/tkinter_expense_manager.py

## Usage
- **Add Expense Records:** Capture expense details through an intuitive form.
- **Manage Expenses:** Perform CRUD operations on expense data.
- **Search and Filter:** Quickly find specific expense records.
- **Visualize Data:** Monthly expenses visualized in bar graphs.
- **SQLite3 Data Storage:** Reliable data management with SQLite3.

## Design and Architecture
- **Model-View-Controller (MVC):** Separates logic, UI, and control for scalability and maintainability.
- **SQLite3 Database:** Lightweight and efficient data management.
- **Pythonic Approach:** The codebase follows Pythonic principles for clarity and ease of maintenance.

## Data Model Schema

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

## Note
This project is developed for educational and demonstration purposes. It's a personal project aimed at showcasing Python and Tkinter capabilities in building desktop applications.

