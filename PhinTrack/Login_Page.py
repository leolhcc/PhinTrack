from PyQt6.QtWidgets import QWidget, QVBoxLayout,QHBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

class Login_Page(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setStyleSheet("""
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
            #login_label {
                color: #29353C;
                font-size: 40px;
                font-weight: bold;
                min-height: 60px;
                margin-bottom: 50px;
            }
            #logo_label, #phintrack_name {
                margin-top: 0px;
                margin-bottom: 20px;
                color: #4C5E69;
            }
        """)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.phin_logo(layout)

        login_label = QLabel("Sign In")
        login_label.setObjectName("login_label")
        login_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(login_label)
        
        #Inputs (email, password)
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        login_button = QPushButton("Login")
        login_button.clicked.connect(main_window.attempt_login)
        
        #Navigation to 'forgot password' and 'create account' pages
        forgot_password_button = QPushButton("Forgot Password?")
        forgot_password_button.clicked.connect(lambda: main_window.stacked_widget.setCurrentWidget(main_window.forgot_password_page))
        create_account_button = QPushButton("Create Account")
        create_account_button.clicked.connect(self.navigate_to_create_account)

        layout.addWidget(self.email_input)
        layout.addWidget(self.password_input)
        layout.addWidget(login_button)
        layout.addWidget(forgot_password_button)
        layout.addWidget(create_account_button)

        self.setLayout(layout)

    #Clear input fields after logging in
    def clear_inputs(self):
        self.email_input.clear()
        self.password_input.clear()

    def navigate_to_create_account(self):
        self.main_window.create_account_page.clear_inputs()
        self.main_window.stacked_widget.setCurrentWidget(self.main_window.create_account_page)

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