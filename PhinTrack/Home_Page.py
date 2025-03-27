from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import csv
import random

class Home_Page(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setStyleSheet("""
            QLabel {
                color: #29353C;
                font-size: 15px;
                font-weight: normal;
            }
            #logo_label, #phintrack_name {
                margin-top: 30px;
                color: #4C5E69;
                font-size: 40px;
                font-weight: bold;
                margin-bottom: 10px; 
                maximum-height: 75px;
            }
            #greet_label {
                color: #29353C;
                font-size: 40px;
                font-weight: bold;
                max-height: 75px;
                margin-top: 10px;
            }    
            #recent_transactions_label {
                background: #DEEFFF;
                border-radius: 8px;
                color: #29353C;
                font-size: 25px;
                font-weight: bold;
                padding: 10px;
                margin-top: 30px;
                margin-bottom: 30px;
                min-width: 400px;
            }
            #balance_label {
                color: #29353C;
                font-size: 25px;
                font-weight: bold;
                padding: 10px;
                margin-top: 30px;
                margin-bottom: 50px;
                min-width: 400px;
                min-height: 80px;   
            }
            #phin_tip {
                background: #DEEFFF;
                border-radius: 8px;
                color: #29353C;
                font-size: 25px;
                font-weight: bold;
                padding: 10px;
                margin-top: 10px;
                margin-bottom: 20px;
            }
            #finance_tip {
                min-height: 75px;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.phin_logo(layout)
        self.setLayout(layout)

        #Greet the user
        self.greet_label = QLabel()
        self.greet_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop) 
        self.greet_label.setObjectName("greet_label")
        layout.addWidget(self.greet_label, stretch=0)
        self.make_greeting()

        #Layout of user's current balance, daily finance tip, and recent transactions
        balance_transactions = QHBoxLayout()
        balance_transactions.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addLayout(balance_transactions)

        #Group current balance display and finance tip display together
        self.balance_tip = QVBoxLayout()
        self.balance_tip.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.balance_tip.setAlignment(Qt.AlignmentFlag.AlignTop)
        balance_transactions.addLayout(self.balance_tip)

        self.balance_label = QLabel()
        self.balance_label.setObjectName("balance_label")
        self.balance_label.setAlignment(Qt.AlignmentFlag.AlignHCenter) 
        self.balance_tip.addWidget(self.balance_label)
        balance_transactions.addSpacing(150)
        self.print_current_balance()

        self.phin_tip = QLabel("Phin's Finance Tip of the Day:")
        self.phin_tip.setObjectName("phin_tip")
        self.phin_tip.setAlignment(Qt.AlignmentFlag.AlignHCenter) 
        self.balance_tip.addWidget(self.phin_tip)

        self.finance_tip = QLabel()
        self.finance_tip.setObjectName("finance_tip")
        self.finance_tip.setAlignment(Qt.AlignmentFlag.AlignHCenter) 
        self.finance_tip.setMaximumWidth(700)
        self.finance_tip.setWordWrap(True)
        self.balance_tip.addWidget(self.finance_tip)
        self.print_finance_tip()

        self.recent_transactions_layout = QVBoxLayout()
        self.recent_transactions_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter) 
        self.recent_transactions_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        balance_transactions.addLayout(self.recent_transactions_layout)

        self.recent_transactions_label = QLabel("Recent Transactions:")
        self.recent_transactions_label.setAlignment(Qt.AlignmentFlag.AlignHCenter) 
        self.recent_transactions_label.setObjectName("recent_transactions_label")
        self.recent_transactions_layout.addWidget(self.recent_transactions_label)
        self.transaction_labels = []
        self.load_recent_transactions()  #Display the five most recent transactions

    def make_greeting(self):
        username = self.main_window.current_user["username"] if self.main_window.is_logged_in else ""    
        self.greet_label.setText(f"Welcome back, {username}!")

    def print_current_balance(self):
        balance = self.main_window.account.get_balance() if self.main_window.is_logged_in else ""
        #Display balance with 2 decimals places
        if not balance == "":
            balance = f"{float(balance):.2f}"
        self.balance_label.setText(f"Current Balance: ${balance}")

    #Choose a random finance tip to display every time user runs the program
    def print_finance_tip(self):
        tips = ["Track your expenses. Keep track of every dollar you spend.",
                "Choose carefully. Every decision has a cost, so be sure to consider your options.",
                "Save. Save more, and keep saving. Practice saving, not spending.",
                "Remember, everything adds up!",
                "Embrace the 50/30/20 Rule! Allocate 50% for essentials, 30% for fun, and 20% to savings—adjust as needed for your situation.",
                "You are in charge. You are responsible for your finances and you should act accordingly.",
                "Watch spending. You control your money, determining how you spend or save it. Pace spending and increase saving by cutting unnecessary expenses.",
                "Ask. Managing your finances is a learning experience, so if you need help, ask. Phin is always here in the Help Center if you need anything.",
                "Understand needs vs. wants. Prioritize spending on what is necessary",
                ]
        random_tip = random.choice(tips)
        self.finance_tip.setText(random_tip)
        self.finance_tip.setObjectName("finance_tip")

    #Read and load the five most recent transactions from user-specific CSV
    def load_recent_transactions(self):
        user_email = self.main_window.current_user["email"]  if self.main_window.is_logged_in else ""
        unique_csv = f"transactions_{user_email}.csv" 
        try:
            with open(unique_csv, "r") as file:
                reader = csv.reader(file)
                transactions = [row for row in reader if row and row[0] == user_email]
                #Sort all of the user's transactions by date, with the most recent date at the top
                transactions.sort(key=lambda x: (self.main_window.transactions_page.date_tuple(x[1]), x[2]), reverse=True)
                self.clear_transaction_labels()
                for row in transactions[:5]:
                    date = row[1]
                    amount = float(row[3])
                    transaction_type = "Deposit" if amount > 0 else "Withdraw"

                    #Display all of the transaction's info as a label
                    amount_label = f"${abs(amount):.2f}"
                    transaction_label = QLabel(f"{date}: ({transaction_type}) {amount_label}  ")
                    transaction_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                    transaction_label.setMaximumHeight(60)
                    transaction_label.setMinimumHeight(40)
                    self.recent_transactions_layout.addWidget(transaction_label)
                    self.transaction_labels.append(transaction_label)
        except FileNotFoundError:
            print("No transactions found.")

    def clear_transaction_labels(self):
        for label in self.transaction_labels:
            self.layout().removeWidget(label)
            label.deleteLater()
        self.transaction_labels.clear()
    
    #Display logo and name
    def phin_logo(self, layout):
        logo_layout = QHBoxLayout()
        logo_layout.setSpacing(10)
        logo_layout.setContentsMargins(0,0,0,0)
        logo_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        logo_label = QLabel()
        phintrack_logo = QPixmap('PhinTrack.png')
        logo_label.setPixmap(phintrack_logo.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        logo_label.setObjectName("logo_label")
        logo_layout.addWidget(logo_label)
        phintrack_name = QLabel("PhinTrack")
        phintrack_name.setMinimumWidth(200)
        phintrack_name.setObjectName("phintrack_name")
        logo_layout.addWidget(phintrack_name)
        layout.addLayout(logo_layout, stretch=0)