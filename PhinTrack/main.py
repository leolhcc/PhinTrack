from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QStackedWidget, QHBoxLayout, QMessageBox
from Account import Account, load_accounts_from_csv
from Transaction import Transaction
from Report import Report
import hashlib
import csv
import os

from Login_Page import Login_Page
from Forgot_Password_Page import Forgot_Password_Page
from Create_Account_Page import Create_Account_Page
from Home_Page import Home_Page
from Transactions_Page import Transactions_Page
from Report_Page import Report_Page
from Help_Page import Help_Page

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        load_accounts_from_csv()
        self.setWindowTitle("Financial Manager")
        self.setGeometry(0, 0, 1400, 800)
        self.is_logged_in = False
        self.account = None
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
            QWidget {
                background-color: #F7F7F7;
                font-family: 'Century Gothic';
                font-size: 14px;
            }        
        """)

        main_layout = QVBoxLayout()
        self.nav_bar = NavigationBar(self)
        main_layout.addWidget(self.nav_bar)
        self.stacked_widget = QStackedWidget()

        #Set up all the pages
        self.login_page = Login_Page(self)
        self.forgot_password_page = Forgot_Password_Page(self)
        self.create_account_page = Create_Account_Page(self)
        self.home_page = Home_Page(self)
        self.transactions_page = Transactions_Page(self)
        self.report_page = Report_Page(self)
        self.help_page = Help_Page(self)

        self.stacked_widget.addWidget(self.login_page)
        self.stacked_widget.addWidget(self.forgot_password_page)
        self.stacked_widget.addWidget(self.create_account_page)
        self.stacked_widget.addWidget(self.home_page)
        self.stacked_widget.addWidget(self.transactions_page)
        self.stacked_widget.addWidget(self.report_page)
        self.stacked_widget.addWidget(self.help_page)

        self.stacked_widget.currentChanged.connect(self.update_nav_bar_visibility)

        main_layout.addWidget(self.stacked_widget)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.update_nav_bar_visibility()

    #Verify login information when user clicks 'Login'
    def attempt_login(self):
        email = self.login_page.email_input.text()
        password = self.login_page.password_input.text()
        hashed_password = hashlib.sha256(password.encode()).hexdigest()  #Secure user's password

        #Find the user's account
        try:
            with open("accounts.csv", "r") as file:
                reader = csv.reader(file)
                for row in reader:
                    if row and row[1] == email and row[2] == hashed_password:
                        #Keep track of who the current user and account is
                        self.is_logged_in = True
                        self.current_user = {
                            "username": row[0],
                            "email": row[1],
                            "password": row[2],
                            "security_question": row[3],
                            "security_answer": row[4],
                            "balance": float(row[5])
                        }
                        self.account = Account(
                            username=self.current_user["username"],
                            email=self.current_user["email"],
                            password=self.current_user["password"],
                            security_question=self.current_user["security_question"],
                            security_answer=self.current_user["security_answer"],
                            init_balance=self.current_user["balance"]
                        )
                        user_transactions_file = f"{email}_transactions.csv"

                        #Load all the transactions from user-specific CSV to their account
                        if os.path.exists(user_transactions_file):
                            with open(user_transactions_file, "r") as transactions_file:
                                transactions_reader = csv.reader(transactions_file)
                                next(transactions_reader)
                                for transaction_row in transactions_reader:
                                    if transaction_row and transaction_row[0] == email:
                                        t = Transaction(
                                            date=transaction_row[1],
                                            time=transaction_row[2],
                                            type="Deposit" if float(transaction_row[3]) > 0 else "Withdraw",
                                            amount=abs(float(transaction_row[3])),
                                            category=transaction_row[4],
                                            description=transaction_row[5],
                                            account=self.account
                                        )
                                        self.account.add_transaction(t)
                        
                        #Set up all the key pages with this account's information
                        self.report_page.set_account(self.account)
                        self.transactions_page.load_saved_categories()
                        self.transactions_page.load_transactions()
                        self.home_page.make_greeting()
                        self.home_page.load_recent_transactions()
                        self.home_page.print_current_balance()
                        self.report_page.report = Report(self.account)
                        self.stacked_widget.setCurrentWidget(self.home_page)
                        return
        except FileNotFoundError:
            print("Accounts file not found.")
        QMessageBox.warning(self, "Error", "Invalid login credentials.")

    #Check if the key pages can be accessed (when user is logged in)
    def check_access(self, page):
        if self.is_logged_in:
            self.stacked_widget.setCurrentWidget(page)

    #Log out + Hide key pages + Clear inputs + Return to login page
    def logout(self):
        self.is_logged_in = False
        self.login_page.clear_inputs()
        self.transactions_page.clear_inputs()
        self.transactions_page.clear_filters()
        self.stacked_widget.setCurrentWidget(self.login_page)
        self.update_nav_bar_visibility()
        self.report_page.clear_reports()

    #Don't show the key pages when user is not logged in yet (still in login/create account/reset password pages)
    def update_nav_bar_visibility(self):
        current_widget = self.stacked_widget.currentWidget()
        print(f"Current widget: {current_widget}")
        if current_widget in [self.login_page, self.forgot_password_page, self.create_account_page]:
            self.nav_bar.hide()
        else:
            self.nav_bar.show()


class NavigationBar(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.setStyleSheet("""
            QPushButton {
                background-color: #58719A;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #44576D;
            }   
        """)

        #Navigation bar layout
        layout = QHBoxLayout()
        home_button = QPushButton("Home")
        home_button.clicked.connect(lambda: main_window.check_access(main_window.home_page))
        transactions_button = QPushButton("Transactions")
        transactions_button.clicked.connect(lambda: main_window.check_access(main_window.transactions_page))
        reports_button = QPushButton("Reports")
        reports_button.clicked.connect(lambda: main_window.check_access(main_window.report_page))
        help_button = QPushButton("Help")
        help_button.clicked.connect(lambda: main_window.check_access(main_window.help_page))
        logout_button = QPushButton("Logout")
        logout_button.clicked.connect(main_window.logout)
        
        layout.addWidget(home_button)
        layout.addWidget(transactions_button)
        layout.addWidget(reports_button)
        layout.addWidget(help_button)
        layout.addWidget(logout_button)
        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()