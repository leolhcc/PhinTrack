from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, QMessageBox, QHBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

from Account import Account, accounts

class Create_Account_Page(QWidget):
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
                margin-bottom: 25px;
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
            #password_reqs_label {
                color: #29353C;
                font-size: 15px;
                font-weight: normal;
                margin-top: 0px;
                margin-bottom: 0px;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.phin_logo(main_layout)

        form_layout = QVBoxLayout()

        create_account_label = QLabel("Create Account")
        create_account_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(create_account_label)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.password_reqs = QLabel("(Password must be at least 8 characters long, contain uppercase and lowercase letters, a number, and a special character.)")
        self.password_reqs.setWordWrap(True)
        self.password_reqs.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.password_reqs.setObjectName("password_reqs_label")
        self.password_reqs.setVisible(False)
        self.password_input.textChanged.connect(self.toggle_password_reqs)

        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Confirm Password")
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.security_question_dropdown = QComboBox()
        self.security_question_dropdown.addItem("Select Security Question")
        self.security_question_dropdown.addItems(["What is the name of your first pet?", "What city were you born in?", "What is your favorite food?", "What is your mother's maiden name?", "What street did you grow up on?"])
        self.security_question_dropdown.setObjectName("securityQuestionDropdown")
        self.security_question_dropdown.setStyleSheet("""
            #securityQuestionDropdown {
                background: #768A96;
                selection-background-color: #44576D; /* hover over answers */
                border: 1px solid #AAC7D8;
                border-radius: 5px;
                max-width: 625px;  
                min-height: 30px;
                padding-left: 10px;
            }
            #securityQuestionDropdown QAbstractItemView {
                background: #768A96;  /* Fix black box issue */
                border: 1px solid #AAC7D8;
                border-radius: 5px;
                max-width: 625px;
                padding-left: 10px;
            }
            #securityQuestionDropdown QAbstractItemView::item:hover {
                background: #44576D;
                color: white;
                max-width: 625px;
                padding-left: 10px;
            }
        """)

        self.security_answer_input = QLineEdit()
        self.security_answer_input.setPlaceholderText("Security Answer")

        create_button = QPushButton("Create Account")
        create_button.clicked.connect(self.create_account)

        #Navigation back to login page
        login_button = QPushButton("Back To Login")
        login_button.setObjectName("login_button")
        login_button.clicked.connect(lambda: self.main_window.stacked_widget.setCurrentWidget(self.main_window.login_page))

        form_layout.addSpacing(20)
        form_layout.addWidget(self.username_input)
        form_layout.addWidget(self.email_input)
        form_layout.addWidget(self.password_reqs)
        form_layout.addWidget(self.password_input)
        form_layout.addWidget(self.confirm_password_input)
        form_layout.addWidget(self.security_question_dropdown)
        form_layout.addWidget(self.security_answer_input)
        form_layout.addWidget(create_button)
        form_layout.addWidget(login_button)

        main_layout.addLayout(form_layout)

    def create_account(self):
        username = self.username_input.text()
        email = self.email_input.text()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        security_question = self.security_question_dropdown.currentText()
        security_answer = self.security_answer_input.text()

        #Make sure all fields are inputted and valid
        if not username or not email or not password or not security_answer:
            QMessageBox.warning(self, "Error", "Please fill out all fields.")
            return

        if security_question == "Select Security Question":
            QMessageBox.warning(self, "Error", "Please select a valid security question.")
            return
        
        if not self.check_username(username):
            QMessageBox.warning(self, "Error", "Please enter a valid username that contains 3-20 characters.")
        
        if not self.check_email(email):
            QMessageBox.warning(self, "Error", "Please enter a valid email address.")
            return
        
        if not password == confirm_password:
            QMessageBox.warning(self, "Error", "Passwords do not match.")
            return
        
        valid, warning = self.check_password(password)
        if not valid:
            QMessageBox.warning(self, "Error", warning)
            return

        if email in [acc.email for acc in accounts]:
            QMessageBox.warning(self, "Error", "This email already exists.")
        else:  #If all fields are valid, create account with the user's inputs
            self.acc = Account(username, email, password, security_question, security_answer, 0)
            self.clear_inputs()  #Clear input fields after creating account
            self.main_window.stacked_widget.setCurrentWidget(self.main_window.login_page)  #Return to login page when done

#Helper functions to check input fields
    def check_username(self, username):
        if " " in username:
            return False
        if len(username) < 3 or len(username) > 20:
            return False
        return True
        
    def check_email(self, email):
        if " " in email:
            return False
        if "@" not in email:
            return False
        split_at = email.split("@")
        if len(split_at) != 2:
            return False
        local, domain = split_at
        if "." not in domain:
            return False
        if domain.startswith(".") or domain.endswith("."):
            return False
        return True
    
    def check_password(self, password):
        special_chars = "!@#$%^&*()_"
        if len(password) < 8:
            return False, "Password must be at least 8 characters long."
        if " " in password:
            return False, "Password cannot contain any spaces."
        if not any(char.isupper() for char in password):
            return False, "Password must contain at least 1 uppercase letter."
        if not any(char.islower() for char in password):
            return False, "Password must contain at least 1 lowercase letter."
        if not any(char.isdigit() for char in password):
            return False, "Password must contain at least 1 number."
        if not any(char in special_chars for char in password):
            return False, "Password must contain at least 1 special character. !@#$%^&*()_"
        return True, ""
    
    #Set the visibility of password requirements
    def toggle_password_reqs(self):
        if self.password_input.text():
            self.password_reqs.setVisible(True)
            print("Password requirements label is visible")
        else:
            self.password_reqs.setVisible(False)
            print("Password requirements label is hidden")

    def clear_inputs(self):
        self.username_input.clear()
        self.email_input.clear()
        self.password_input.clear()
        self.confirm_password_input.clear()
        self.security_answer_input.clear()
        self.security_question_dropdown.setCurrentIndex(0)
    
    #Display the logo and name
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