from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QComboBox, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem, QTextEdit
from Transaction import Transaction
from Account import existing_transactions, export_transactions_to_csv, accounts
from Account import Account
import csv
import re
from datetime import datetime
from Report_Page import Report_Page

#Format money values with two decimal places
def money_number(num):
    if isinstance(num, (int, float)):
        num = str(num)
    if num:
        whole,decimal = num.split(".")
        if len(decimal) == 1:
            return whole + "." + decimal + "0"
        else:
            return num

is_editing = False

class Transactions_Page(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setStyleSheet("""
            QMessageBox QLabel {
                color: #29353C;
                font-size: 14px;
                font-weight: normal; 
                margin-bottom: 0px;
            }
            QMessageBox QPushButton {
                background-color: #58719A;
                color: white;
                padding: 5px;
                border-radius: 5px;
            }
            QMessageBox QPushButton:hover {
                background-color: #CCDEE5
            }
            QLabel {
                color: #29353C;
                font-size: 20px;
            }
            QLineEdit {
                background: #F3F6F4;
                padding: 5px;
                color: #29353C;
                border: 1px solid #AAC7D8;
                border-radius: 5px;
            }
            QTextEdit {
                background: #F3F6F4;
                padding: 5px;
                color: #29353C;
                border: 1px solid #AAC7D8;
                border-radius: 5px;
            }
            QPushButton {
                background: #768A96;
                color: white;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #CCDEE5;
            }
            QComboBox {
                background: #768A96;
                selection-background-color: #44576D; /* hover over answers */
                border: 1px solid #AAC7D8;
                border-radius: 5px;
                min-height: 30px;
                min-width: 90px;
                padding-left: 5px;
            }
            QComboBox QAbstractItemView {
                background: #768A96;  /* Fix black box issue */
                border: 1px solid #AAC7D8;
                border-radius: 5px;
                padding-left: 5px;
            }
            QComboBox QAbstractItemView::item:hover {
                background: #44576D;
                color: white;
                padding-left: 5px;
            }
            #min_filter, #max_filter {
                max-width: 125px;
            }
            #date_filter, #time_filter {
                max-width: 150px;
            }
            #category_filter, #description_filter {
                max-width: 175px;
            }
        """)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Transactions Page"))
        
        #Set up all the required input fields
        self.datetime = QHBoxLayout()
        self.date_input = QLineEdit()
        self.date_input.setPlaceholderText("Date (MM/DD/YYYY)")
        self.time_input = QLineEdit()
        self.time_input.setPlaceholderText("Time (HH:MM)")
        self.datetime.addWidget(self.date_input)
        self.datetime.addWidget(self.time_input)
        
        self.type_amount_layout = QHBoxLayout()
        self.type_dropdown = QComboBox()
        self.type_amount_layout.addWidget(self.type_dropdown)
        self.type_dropdown.addItems(["Deposit", "Withdraw"])
        self.type_dropdown.currentIndexChanged.connect(self.update_category_options)
        self.type_dropdown.setObjectName("typeDropdown")
        self.type_dropdown.setStyleSheet("""
            #typeDropdown {
                min-width: 125px;
            }
        """)
        
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Amount")
        self.type_amount_layout.addWidget(self.amount_input)

        self.category_dropdown = QComboBox()
        #Default categories
        self.income_categories = ["Salary", "Gift", "Investment", "Other"]
        self.expense_categories = ["Food", "Transport", "Entertainment", "Other"]
        self.category_dropdown.addItems(self.income_categories)
        self.category_dropdown.currentIndexChanged.connect(self.check_other_category)
        
        #Custom Categories
        self.other_category_input = QLineEdit()
        self.other_category_input.setPlaceholderText("Enter new category")
        self.other_category_input.setVisible(False)
        
        #Optional description
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Description")
        self.description_input.setObjectName("descriptionInput")
        self.description_input.setStyleSheet("""
            #descriptionInput {
                max-height: 50px;
            }
        """)
        
        self.add_button = QPushButton("Add Transaction")
        self.add_button.clicked.connect(self.add_transaction)
        
        self.remove_button = QPushButton("Remove Transaction")
        self.remove_button.clicked.connect(self.remove_transaction)

        self.edit_button = QPushButton("Edit Transaction")
        self.edit_button.clicked.connect(self.edit_transaction)

        #Search and filter options (can filter by multiple fields at a time)
        self.filter_widgets = []
        filter_layout = QHBoxLayout()

        self.date_filter = QLineEdit()
        self.date_filter.setPlaceholderText("MM/DD/YYYY")
        self.date_filter.setObjectName("date_filter")
        self.date_filter.textChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.date_filter)
        self.filter_widgets.append(self.date_filter)

        self.time_filter = QLineEdit()
        self.time_filter.setPlaceholderText("HH:MM")
        self.time_filter.setObjectName("time_filter")
        self.time_filter.textChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.time_filter)
        self.filter_widgets.append(self.time_filter)

        self.type_filter = QComboBox()
        self.type_filter.addItems(["","Deposit", "Withdraw"])
        self.type_filter.currentIndexChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.type_filter)
        self.filter_widgets.append(self.type_filter)

        self.min_filter = QLineEdit()
        self.min_filter.setPlaceholderText("Min. Amount")
        self.min_filter.setObjectName("min_filter")
        self.min_filter.textChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.min_filter)
        self.filter_widgets.append(self.min_filter)

        self.max_filter = QLineEdit()
        self.max_filter.setPlaceholderText("Max. Amount")
        self.max_filter.setObjectName("max_filter")
        self.max_filter.textChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.max_filter)
        self.filter_widgets.append(self.max_filter)

        self.category_filter = QLineEdit()
        self.category_filter.setPlaceholderText("Category")
        self.category_filter.setObjectName("category_filter")
        self.update_category_filter()
        self.category_filter.textChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.category_filter)
        self.filter_widgets.append(self.category_filter)

        self.description_filter = QLineEdit()
        self.description_filter.setPlaceholderText("Search description...")
        self.description_filter.setObjectName("description_filter")
        self.description_filter.textChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.description_filter)
        self.filter_widgets.append(self.description_filter)

        self.clear_button = QPushButton("Clear Filters")
        self.clear_button.clicked.connect(self.clear_filters)
        filter_layout.addWidget(self.clear_button)

        #Set up transaction history table
        self.transactions_table = QTableWidget()
        self.transactions_table.setColumnCount(6)
        self.transactions_table.setHorizontalHeaderLabels(["Date", "Time", "Type", "Amount", "Category", "Description"])
        self.transactions_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.transactions_table.setStyleSheet("""
            QTableWidget {
                background-color: #2c3e50;
                color: white;
                gridline-color: #44576D;
                font-size: 14px;
                border: 2px solid #768A96;
                border-radius: 5px;
                alternate-background-color: #3e5366;
            }
            QHeaderView::section {
                background-color: #44576D;
                color: white;
                padding: 3px;
                border: 1px solid #2c3e50;
                font-weight: bold;
                text-align: center;
            }
            QTableWidget::item {
                background-color: #F4F2EB;
                color: #29353C;
                padding: 5px;
                border: none;
            }
            QTableWidget::item:hover {
                background-color: #c5e1ef;
            }
            QTableWidget::item:selected {
                background-color: #44576D;
                color: white;
            }                            
            QScrollBar:vertical {
                border: none;
                background: #2c3e50;
                width: 10px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: #768A96;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                background: none;
                border: none;
            }
        """)

        self.load_transactions()
        self.load_saved_categories()

        layout.addLayout(self.datetime)
        layout.addLayout(self.type_amount_layout)
        layout.addWidget(self.category_dropdown)
        layout.addWidget(self.other_category_input)
        layout.addWidget(self.description_input)
        layout.addWidget(self.add_button)
        layout.addWidget(self.remove_button)
        layout.addWidget(self.edit_button)
        layout.addLayout(filter_layout)
        layout.addWidget(self.transactions_table)
        self.setLayout(layout)

    def is_valid_date(self, date_string):
        try:
            date = datetime.strptime(date_string, "%m/%d/%Y")
            #Make sure it's a reasonable year for students
            if not (1980 <= date.year <= 2025):
                return False
            cutoff_date = datetime.now().date()
            #Make sure input date isn't in the future
            if date.date() > cutoff_date:
                return False
            return True
        except ValueError:
            return False
        
    def is_valid_time(self, date_string, time_string):
        try:
            date = datetime.strptime(date_string, "%m/%d/%Y")
            time = datetime.strptime(time_string, "%H:%M").time()
            
            current_datetime = datetime.now()
            input_datetime = datetime.combine(date, time)

            #Ensure datetime isn't in the future
            if input_datetime > current_datetime:
                return False
            
            return True
        except ValueError:
            #Handle invalid format or out-of-range values
            return False

    def update_category_options(self):
        self.category_dropdown.clear()
        if self.type_dropdown.currentText() == "Deposit":
            self.category_dropdown.addItems(self.income_categories)
        else:
            self.category_dropdown.addItems(self.expense_categories)

    #A new input box pops up when user chooses 'Other' for category
    def check_other_category(self):
        if self.category_dropdown.currentText() == "Other":
            self.other_category_input.setVisible(True)
        else:
            self.other_category_input.setVisible(False)
    
    def add_transaction(self):
        global is_editing
        user_email = self.main_window.current_user["email"] if self.main_window.is_logged_in else ""
        date = self.date_input.text()
        time = self.time_input.text()
        trans_type = self.type_dropdown.currentText()
        amount = self.amount_input.text()
        category = self.category_dropdown.currentText()
        description = self.description_input.toPlainText()

        #Input validation (correct format & logical)
        if not user_email or not date or not time or not trans_type or not amount or not category:
            QMessageBox.warning(self, "Error", "Please fill out all fields.")
            return
        if not self.is_valid_date(date):
            QMessageBox.warning(self, "Error", "Enter a valid date.")
            return
        if not self.is_valid_time(date, time):
            QMessageBox.warning(self, "Error", "Enter a valid time.")
            return
        money_pattern = r'^\d+(\.\d{2})?$'  #Match using regex
        if bool(re.match(money_pattern, amount)) and float(amount) != 0.0:
            amount = float(amount)
        else:
            QMessageBox.warning(self, "Error", "Enter a valid numerical amount of money.")
            return

        if category == "Other":
            new_category = self.other_category_input.text().strip()
            if new_category and any(c.isalpha() for c in new_category) and not new_category.isspace():
                for ic in self.income_categories:
                    if new_category.lower() == ic.lower():
                        QMessageBox.warning(self, "Error", "This category already exists.")
                        return
                for ec in self.expense_categories:
                    if new_category.lower() == ec.lower():
                        QMessageBox.warning(self, "Error", "This category already exists.")
                        return
                category = new_category
                self.save_new_category(user_email, new_category, trans_type)
            else:
                QMessageBox.warning(self, "Error", "Enter a valid category.")
                self.clear_inputs()
                return
                
        if not description:
            description = "N/A"

        t = Transaction(
            date=date,
            time=time,
            type=trans_type,
            amount=float(amount),
            category=category,
            description=description,
            account=self.main_window.account
        )

        filename = f"transactions_{user_email}.csv"
        transactions = self.load_transactions_from_csv(filename)
        self.main_window.account.transactions = transactions
        #Check if adding a withdrawal gets a negative balance at any point of transaction history (use a different check for editing transactions)
        if trans_type == "Withdraw" and not self.main_window.account.can_add_withdrawal(t) and not is_editing:
            QMessageBox.warning(self, "Error", "Insufficient Funds To Withdraw.")
            return

        #If all inputs are valid, we're ready to add a transaction
        for acc in accounts:
            if acc.email == self.main_window.account.email:
                acc.balance += (t.get_amount() * t.get_type())
                break
        
        #Update all relevant data storage
        self.main_window.account.add_transaction(t)
        self.main_window.current_user["balance"] += (float(amount) * (1.0 if trans_type == "Deposit" else -1.0))
        self.main_window.home_page.print_current_balance()
        export_transactions_to_csv(self.main_window.account)

        #Immediately update recent transactions (Home Page) and reports (Reports Page)
        self.main_window.home_page.load_recent_transactions()
        self.main_window.report_page.update_reports()
        self.load_transactions()
        if not is_editing:
            QMessageBox.information(self, "Success", "Transaction added successfully.")
        self.clear_inputs()

    def remove_transaction(self):
        global is_editing
        #Select a transaction in the transactions table to delete
        selected_row = self.transactions_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Error", "Please select a transaction to remove.")
            return
        
        #Store the data of the selected transaction in transaction_to_remove
        transaction_data = []
        for col in range(self.transactions_table.columnCount()):
            item = self.transactions_table.item(selected_row, col)
            transaction_data.append(item.text() if item else "")
        transaction_to_remove = None
        for transaction in existing_transactions:
            if (transaction.date == transaction_data[0] and
                transaction.time == transaction_data[1] and
                ("Deposit" if transaction.deposit else "Withdraw") == transaction_data[2] and
                float(transaction.amount) == float(transaction_data[3]) and
                transaction.category == transaction_data[4] and
                transaction.description == transaction_data[5]):
                transaction_to_remove = transaction
                break
        if not transaction_to_remove:
            QMessageBox.warning(self, "Error", "Selected transaction could not be found.")
            return
        
        #Check if removing the deposit is valid (Invalid if the balance is negative at any point in history)
        filename = f"transactions_{self.main_window.current_user["email"]}.csv"
        transactions = self.load_transactions_from_csv(filename)
        self.main_window.account.transactions = transactions
        if transaction_to_remove.deposit and not is_editing and not self.main_window.account.can_remove_deposit(transaction_to_remove):
            QMessageBox.warning(self, "Error", "Insufficient Funds To Remove Deposit.")
            return

        #Proceed when the transaction is ok to remove
        for acc in accounts:
            if acc.email == self.main_window.account.email:
                acc.balance -= (transaction_to_remove.get_amount() * transaction_to_remove.get_type())  #Update account balance in accounts list (Transaction.py)
                break

        #Update all relevant data
        self.main_window.account.remove_transaction(transaction_to_remove)
        self.main_window.current_user["balance"] -= (float(transaction_to_remove.amount) * (1.0 if transaction_to_remove.deposit else -1.0))
        self.main_window.home_page.print_current_balance()
        self.load_transactions()
        #Immediately update recent transactions (home page) and reports (reports page)
        self.main_window.home_page.load_recent_transactions()
        self.main_window.report_page.update_reports()
        if not is_editing:
            QMessageBox.information(self, "Success", "Transaction removed successfully.")

    #Edit_transaction part 1 (Gathering info)
    def edit_transaction(self):
        global is_editing
        is_editing = True
        #Select a transaction in the transactions table to edit
        selected_transaction = self.transactions_table.currentRow()
        if selected_transaction < 0:
            QMessageBox.warning(self, "Error", "Please select a transaction to edit.")
            return

        #Store the data of the transaction that user wants to edit in old_transaction
        transaction_data = []
        for col in range(self.transactions_table.columnCount()):
            item = self.transactions_table.item(selected_transaction, col)
            transaction_data.append(item.text() if item else "")
        user_email = self.main_window.current_user["email"] if self.main_window.is_logged_in else ""
        filename = f"transactions_{user_email}.csv"
        transactions = self.load_transactions_from_csv(filename)
        self.main_window.account.transactions = transactions
        old_transaction = None
        for transaction in transactions:
            if (transaction.date == transaction_data[0] and
                transaction.time == transaction_data[1] and
                ("Deposit" if transaction.deposit else "Withdraw") == transaction_data[2] and
                float(transaction.amount) == float(transaction_data[3]) and
                transaction.category == transaction_data[4] and
                transaction.description == transaction_data[5]):
                old_transaction = transaction
                break

        if not old_transaction:
            QMessageBox.warning(self, "Error", "Selected transaction could not be found.")
            return

        #Load the transactions's data to the input fields
        self.date_input.setText(transaction_data[0])
        self.time_input.setText(transaction_data[1])
        self.type_dropdown.setCurrentText(transaction_data[2])
        self.amount_input.setText(transaction_data[3])
        self.category_dropdown.setCurrentText(transaction_data[4])
        self.description_input.setText(transaction_data[5])

        #If the 'Save Changes' button is clicked, proceed to the actual editing of transaction
        self.add_button.setText("Save Changes")
        self.add_button.clicked.disconnect()
        self.add_button.clicked.connect(lambda: self.save_edited_transaction(old_transaction))
        is_editing = False

    #Edit_transaction part 2 (Changing transaction info)
    def save_edited_transaction(self, old_transaction):
        global is_editing
        is_editing = True

        #Create the new transaction from input fields
        new_transaction = Transaction(
            date=self.date_input.text(),
            time=self.time_input.text(),
            type=self.type_dropdown.currentText(),
            amount=float(self.amount_input.text()),
            category=self.category_dropdown.currentText(),
            description=self.description_input.toPlainText(),
            account=self.main_window.account
        )

        #Check if the changes are valid (balance is >= 0 at all points in transactions history)
        if not self.main_window.account.can_edit(old_transaction, new_transaction):
            QMessageBox.warning(self, "Error", "Insufficient Funds To Change.")
            is_editing = False
            self.clear_inputs()
            self.add_button.setText("Add Transaction")
            return
        
        #Remove the old transaction from existing_transactions
        if old_transaction in existing_transactions:
            self.remove_transaction()

        self.date_input.setText(new_transaction.date)
        self.time_input.setText(new_transaction.time)
        self.type_dropdown.setCurrentText("Deposit" if new_transaction.deposit else "Withdraw")
        self.amount_input.setText(money_number(str(new_transaction.amount)))
        self.category_dropdown.setCurrentText(new_transaction.category)
        self.description_input.setText(new_transaction.description)

        #Add the new transaction to existing_transactions with the inputs above
        self.add_transaction()

        #Export transactions to the user-specific file
        export_transactions_to_csv(self.main_window.account)

        #Update the UI
        self.main_window.home_page.print_current_balance()
        self.main_window.home_page.load_recent_transactions()
        self.main_window.report_page.update_reports()
        self.add_button.setText("Add Transaction")
        self.add_button.clicked.disconnect()
        self.add_button.clicked.connect(self.add_transaction)
        self.clear_inputs()
        self.load_transactions()
        QMessageBox.information(self, "Success", "Transaction updated successfully.")
        is_editing = False

    #Get user's transactions from user-specific CSV
    def load_transactions_from_csv(self, filename):
        transactions = []
        try:
            with open(filename, "r") as file:
                reader = csv.reader(file)
                next(reader)  #Skip the header row
                for row in reader:
                    if row:  #Ensure the row is not empty
                        transaction = Transaction(
                            date=row[1],
                            time=row[2],
                            type="Deposit" if float(row[3]) > 0 else "Withdraw",
                            amount=abs(float(row[3])),
                            category=row[4],
                            description=row[5],
                            account=self.main_window.account
                        )
                        transactions.append(transaction)
        except FileNotFoundError:
            print(f"No transactions found in {filename}.")
        return transactions

    #Update the transactions table to only display the transactions that match the filters
    def apply_filters(self):
        #Obtain the filters' info
        date_text = self.date_filter.text().strip()
        time_text = self.time_filter.text().strip()
        selected_type = self.type_filter.currentText()
        min_amount = self.min_filter.text().strip()
        max_amount = self.max_filter.text().strip()
        category_text = self.category_filter.text().strip().lower()
        description_text = self.description_filter.text().strip().lower()

        min_amount = float(min_amount) if min_amount else None
        max_amount = float(max_amount) if max_amount else None

        #Check for the transactions that match the filters
        for row in range(self.transactions_table.rowCount()):
            date = self.transactions_table.item(row, 0).text().strip()
            time = self.transactions_table.item(row, 1).text().strip()
            transaction_type = self.transactions_table.item(row, 2).text().strip()
            amount = float(self.transactions_table.item(row, 3).text())
            category = self.transactions_table.item(row, 4).text().strip().lower()
            description = self.transactions_table.item(row, 5).text().strip().lower()

            #Match status is True by default when there's no user input
            match_date = date.startswith(date_text) if date_text else True
            match_time = time.startswith(time_text) if time_text else True
            match_type = selected_type == "" or transaction_type == selected_type if selected_type else True
            match_category = category_text in category if category_text else True
            match_description = description_text in description if description_text else True

            match_amount = True
            if min_amount is not None:
                match_amount = amount >= min_amount
            if max_amount is not None:
                match_amount = match_amount and amount <= max_amount

            #Temporarily hide the transactions that don't match the filters (until user clears the filters)
            self.transactions_table.setRowHidden(row, not (match_date and match_time and match_type and match_amount and match_category and match_description))

    #Clear filter input fields (called when 'Clear Filters' button is clicked)
    def clear_filters(self):
        for widget in self.filter_widgets:
            if isinstance(widget, QLineEdit):
                widget.clear()
            elif isinstance(widget, QComboBox):
                widget.setCurrentIndex(0)
        self.apply_filters()

    #Updates the category dropdown menu based on the selected transaction type
    def update_category_filter(self):
        self.category_filter.clear()
        selected_type = self.type_filter.currentText()

        #If 'Deposit' is selected, display income categories
        if selected_type == "Deposit":
            self.category_filter.addItems(self.income_categories)
        #If 'Withdraw' is selected, display expense categories
        elif selected_type == "Withdraw":
            self.category_filter.addItems(self.expense_categories)
    
    #Saves a new category to a user-specific CSV file if it doesn't already exist
    #Also updates the relevant category list
    def save_new_category(self, user_email, category, trans_type):
        filename = f"categories_{user_email}.csv"
        try:
            existing_categories = []
            with open(filename, "r") as file:
                reader = csv.reader(file)
                existing_categories = [row[0] for row in reader if len(row) == 2]
            if category not in existing_categories:  #Save new category
                with open(filename, "a", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow([category, trans_type])
                #Update corresponding categories list
                if trans_type == "Deposit" and category not in self.income_categories:
                    self.income_categories.append(category)
                elif trans_type == "Withdraw" and category not in self.expense_categories:
                    self.expense_categories.append(category)
            self.update_category_options()
        except Exception as e:
            print(f"Error saving category: {e}")

    #Loads saved categories from user-specific CSV file
    def load_saved_categories(self):
        user_email = self.main_window.current_user["email"] if self.main_window.is_logged_in else ""  
        filename = f"categories_{user_email}.csv"
        self.income_categories = ["Salary", "Gift", "Investment", "Other"]
        self.expense_categories = ["Food", "Transport", "Entertainment", "Other"]
        try:
            with open(filename, "r") as file:
                reader = csv.reader(file)
                for row in reader:
                    if len(row) == 2:
                        category, trans_type = row
                        if trans_type == "Deposit" and category not in self.income_categories:
                            self.income_categories.append(category)
                        elif trans_type == "Withdraw" and category not in self.expense_categories:
                            self.expense_categories.append(category)
            self.update_category_options()
        except FileNotFoundError:
            print(f"No saved categories found for {user_email}.")
        except Exception as e:
            print(f"Error loading categories: {e}")

    def date_tuple(self, date):
        month, day, year = date.split("/")
        return int(year), int(month), int(day)

    def load_transactions(self):
        user_email = self.main_window.current_user["email"] if self.main_window.is_logged_in else ""
        filename = f"transactions_{user_email}.csv"  #User-specific file

        try:
            #Clear existing_transactions and load transactions for the logged-in user
            existing_transactions.clear()  #Clear the list before loading
            with open(filename, "r") as file:
                reader = csv.reader(file)
                next(reader)  #Skip the header row
                for row in reader:
                    if row and row[0] == user_email:  #Only load transactions for the logged-in user
                        transaction = Transaction(
                            date=row[1],
                            time=row[2],
                            type="Deposit" if float(row[3]) > 0 else "Withdraw",
                            amount=abs(float(row[3])),
                            category=row[4],
                            description=row[5],
                            account=self.main_window.account
                        )
                        existing_transactions.append(transaction)  #Add to existing_transactions

            #Sort transactions by date and time (oldest first, most recent last)
            existing_transactions.sort(
                key=lambda t: (
                    self.date_tuple(t.date),  #Sort by date (year, month, day)
                    tuple(map(int, t.time.split(":")))  #Sort by time (hour, minute)
                )
            )

            # Update the table with the logged-in user's transactions
            self.transactions_table.setRowCount(len(existing_transactions))
            for row_idx, transaction in enumerate(existing_transactions):
                self.transactions_table.setItem(row_idx, 0, QTableWidgetItem(transaction.date))
                self.transactions_table.setItem(row_idx, 1, QTableWidgetItem(transaction.time))
                self.transactions_table.setItem(row_idx, 2, QTableWidgetItem("Deposit" if transaction.deposit else "Withdraw"))
                self.transactions_table.setItem(row_idx, 3, QTableWidgetItem(money_number(str(transaction.amount))))
                self.transactions_table.setItem(row_idx, 4, QTableWidgetItem(transaction.category))
                self.transactions_table.setItem(row_idx, 5, QTableWidgetItem(transaction.description))

        except FileNotFoundError:
            print(f"No transactions found for {user_email}.")

    def clear_inputs(self):
        self.date_input.clear()
        self.time_input.clear()
        self.amount_input.clear()
        self.description_input.clear()
        self.other_category_input.clear()