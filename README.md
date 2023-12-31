# Expense Manager

## Description
Expense Manager is a personal project developed using Python and Tkinter, designed for efficient management of personal or business expenses. It features a SQLite3 database for data persistence.

## Technical Features
- **SQLite3 Database Integration:** Utilizes SQLite3 for data storage and retrieval.
- **Python & Tkinter:** Built with Python's standard GUI toolkit, Tkinter, for user interface.
- **MVC Design Pattern:** Implements the Model-View-Controller (MVC) design pattern.
- **Matplotlib Integration:** Includes Matplotlib for rendering graphical representations of expenses.
- **Data Validation:** Incorporates thorough validation checks to maintain data integrity.

## Installation

### Prerequisites
- Python 3.x
- Virtual environment tool

### Setup and Virtual Environment
1. **Clone the repository:**
```
git clone https://github.com/your-github-username/tkinter_expense_manager.git
```
2. **Navigate to the project directory:**
```
cd tkinter_expense_manager
```
3. **Create a virtual environment:**
```
python -m venv expense_manager
```
4. **Activate the virtual environment:**
- On Windows:
  ```
  .\expense_manager\Scripts\activate
  ```
- On Unix or MacOS:
  ```
  source expense_manager/bin/activate
  ```
5. **Install dependencies:**
```
pip install -r requirements.txt
```
6. **Run the application:**
```
python app/tkinter_expense_manager.py.py
```
## Usage
- **Add Expense Records:** Input details of expenses via a form interface.
- **Manage Expenses:** Perform CRUD operations - Create, Read, Update, and Delete.
- **Search and Filter:** Utilize the search feature for quick access to records.
- **Data Visualization:** View monthly expenses in a graphical format.
- **Data Storage:** All data is stored and managed through a SQLite3 database.

## Design and Architecture
- **MVC Pattern:** Separates the application logic (Model), UI layer (View), and the control layer (Controller) for better maintainability and scalability.
- **SQLite3 Database:** A lightweight database used for storing application data.
- **Pythonic Principles:** The application adheres to Pythonic principles, making it straightforward to understand and modify.

## Data model

| Column             | Data Type | Properties                  |
|--------------------|-----------|-----------------------------|
| id                 | INTEGER   | PRIMARY KEY, AUTOINCREMENT  |
| producto_servicio  | TEXT      |                             |
| cantidad           | INTEGER   |                             |
| monto              | FLOAT     |                             |
| responsable        | TEXT      |                             |
| subtotal           | FLOAT     |                             |
| rubro              | TEXT      |                             |
| proveedor          | TEXT      |                             |
| medio_de_pago      | TEXT      |                             |
| fecha              | DATE      |                             |
| vencimiento        | DATE      |                             |

## Note
This is a personal project, designed and developed for educational and demonstrational purposes.
