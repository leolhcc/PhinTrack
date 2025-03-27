from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import csv
import hashlib
from Create_Account_Page import Create_Account_Page

class Forgot_Password_Page(QWidget):
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
                font-size: 40px;
                font-weight: bold;
                min-height: 60px;
                margin-bottom: 50px;
            }
            QLineEdit {
                padding: 5px;
                color: #29353C;
                border: 1px solid #AAC7D8;
                border-radius: 5px;
                font-size: 14px;
                max-width: 620px;
            }
            QPushButton {
                background-color: #768A96;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                max-width: 600px;
            }
            QPushButton:hover {
                background-color: #44576D;
            }
            #logo_label, #phintrack_name {
                margin-top: 0px;
                margin-bottom: 20px;
                color: #4C5E69;
            }
            #security_question_label {
                color: #29353C;
                font-size: 15px;
                font-weight: normal;
                margin-top: 0px;
                margin-bottom: 0px;
            }
            #password_reqs {
                color: #29353C;
                font-size: 15px;
                font-weight: normal;
                margin-top: 0px;
                margin-bottom: 0px;           
            }
            
        """)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.phin_logo(layout)

        forgot_password_label = QLabel("Forgot Password")
        forgot_password_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(forgot_password_label)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")

        self.security_question_label = QLabel("")
        self.security_question_label.setObjectName("security_question_label")
        self.security_question_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.security_question_label.setVisible(False)

        self.security_answer_input = QLineEdit()
        self.security_answer_input.setPlaceholderText("Security Answer")

        self.new_password_input = QLineEdit()
        self.new_password_input.setPlaceholderText("New Password")
        self.new_password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.password_reqs = QLabel("(Password must be at least 8 characters long, contain uppercase and lowercase letters, a number, and a special character.)")
        self.password_reqs.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.password_reqs.setWordWrap(True)
        self.password_reqs.setVisible(False)  #Password requirements are shown only when user types inside the 'New Password' box
        self.password_reqs.setObjectName("password_reqs")
        self.new_password_input.textChanged.connect(self.toggle_password_reqs)

        reset_button = QPushButton("Reset Password")
        reset_button.clicked.connect(self.reset_password)

        #Navigation back to login page
        login_button = QPushButton("Back To Login")
        login_button.clicked.connect(lambda: self.main_window.stacked_widget.setCurrentWidget(self.main_window.login_page))
        
        layout.addWidget(self.email_input)
        layout.addWidget(self.security_question_label)
        layout.addWidget(self.security_answer_input)
        layout.addWidget(self.password_reqs)
        layout.addWidget(self.new_password_input)
        layout.addWidget(reset_button)
        layout.addWidget(login_button)

        self.setLayout(layout)
        self.email_input.textChanged.connect(self.load_security_question)

    #Security question is shown only when the email that's entered exists in our database
    def load_security_question(self):
        email = self.email_input.text()
        try:
            with open("accounts.csv", "r") as file:
                reader = csv.reader(file)
                for row in reader:
                    if row and row[1] == email:
                        self.security_question_label.setText(row[3])
                        self.security_question_label.setVisible(True)
                        return
        except FileNotFoundError:
            pass
        self.security_question_label.setText("")
        self.security_question_label.setVisible(False)

    #Resets account's password if security answer is correct
    def reset_password(self):
        #Get inputs and validate them
        email = self.email_input.text()
        security_answer = self.security_answer_input.text()
        new_password = self.new_password_input.text()
        valid, warning = Create_Account_Page.check_password(self, new_password)
        if not valid:
            QMessageBox.warning(self, "Error", warning)
            return
        hashed_new_password = hashlib.sha256(new_password.encode()).hexdigest()
        accounts = []

        #Read from account database (CSV)
        try:
            with open("accounts.csv", "r") as file:
                reader = csv.reader(file)
                accounts = [row for row in reader]  #Copy all account data from CSV to accounts list
                for row in accounts:
                    if row and row[1] == email and row[4] == security_answer:  #Check if this account is the one that needs change and that answers match
                        row[2] = hashed_new_password  #Change password in accounts list
                        #Overwrite accounts.csv with the list of copied data and single password change
                        with open("accounts.csv", "w", newline="") as file:
                            writer = csv.writer(file)
                            writer.writerows(accounts)
                        QMessageBox.information(self, "Success", "Password reset successfully.")
                        self.main_window.stacked_widget.setCurrentWidget(self.main_window.login_page)
                        return
        except FileNotFoundError:
            pass
        QMessageBox.warning(self, "Error", "Incorrect security answer.")
    
    #Sets the visibility of password requirements label
    def toggle_password_reqs(self):
        if self.new_password_input.text():
            self.password_reqs.setVisible(True)
        else:
            self.password_reqs.setVisible(False)
    
    #Display logo and name
    def phin_logo(self, layout):
        logo_layout = QHBoxLayout()
        logo_layout.setSpacing(5)
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
        layout.addLayout(logo_layout)