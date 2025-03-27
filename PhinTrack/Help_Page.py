from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QScrollArea, QPushButton
from PyQt6.QtCore import Qt

class Help_Page(QWidget):
  def __init__(self, main_window):
    super().__init__()
    self.main_window = main_window
    self.setStyleSheet("""
      QLabel {
        color: #29353C;
        font-size: 15px;
        font-weight: normal;
        min-width: 1000px;
      }
      QPushButton {
        background-color: #768A96;
        color: white;
        padding: 8px 16px;
        border: none;
        border-radius: 5px;
        font-size: 14px;
        min-width: 1000px;
      }
      QPushButton:hover {
        background-color: #44576D;
      }
      QLineEdit {
        background-color: #f3f6f4;
        padding: 5px;
        color: #29353C;
        border: 1px solid #AAC7D8;
        border-radius: 5px;
        font-size: 14px;
        max-width: 1020px;
        margin-top: 0px;
      }
      #help_center_label {
        color: #29353C;
        font-size: 40px;
        font-weight: bold;
        margin-top: 0px;
        margin-bottom: 30px;
      }
      #faq_label {
        color: #29353C;
        font-size: 30px;
        font-weight: bold;
        margin-bottom: 10px; 
      }
      #chatbot_label {
        color: #29353C;
        font-size: 25px;
        font-weight: bold;
        min-height: 50px;
        margin-top: 30px;
        margin-bottom: 0px;
      }
      #response_output {
        color: #29353C;
        font-size: 15px;
        font-weight: normal;
        margin-bottom: 50px;                 
      }
    """)

    self.setup_layout()
  
  def setup_layout(self):
    layout = QVBoxLayout()
    layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    scroll_page = QScrollArea()
    scroll_page.setWidgetResizable(True)
    scroll_help = QWidget()
    scroll_layout = QVBoxLayout(scroll_help)
    scroll_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

    help_center_label = QLabel("PhinTrack Help Center")
    help_center_label.setObjectName("help_center_label")
    help_center_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
    scroll_layout.addWidget(help_center_label)

    faq_label = QLabel("Frequently Asked Questions")
    faq_label.setObjectName("faq_label")
    faq_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
    scroll_layout.addWidget(faq_label)

    #Display all FAQs with answers
    self.add_faq_label(scroll_layout, "What are the main features of this program?", "PhinTrack allows you to manage your personal finances by tracking account balances, income and expenses.")
    self.add_faq_label(scroll_layout, "How do I add a transaction?", "To add a transaction, go to the Transactions Page, enter the transaction's information, and click 'Add Transaction'.")
    self.add_faq_label(scroll_layout, "Can I delete or edit an existing transaction?", "Yes, you may delete or edit an existing transaction. \nDelete a transaction: click on the transaction you'd like to remove, and click 'Remove Transaction'. \nEdit a transaction: click on the transaction you'd like to edit, click 'Edit Transaction', edit the information, and click 'Save Changes'.")
    self.add_faq_label(scroll_layout, "How can I access the details of a previous transaction?", "You may view all of your transactions in the Transactions Page. Use the search or filter options to narrow your transaction history list.")
    self.add_faq_label(scroll_layout, "Where can I see summaries of my income and expenses?", "You can view detailed summaries in the Reports Page. Click on a time period to view a summary for that period.")
    self.add_faq_label(scroll_layout, "Can I create my own custom categories for income or expenses?", "Yes, you can create your own categories. When adding a new transaction, select 'Other', and enter your desired category.")

    #Chatbot for answering user's questions
    chatbot_label = QLabel("Couldn't find what you're looking for? Ask Phin a question.")
    chatbot_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
    chatbot_label.setObjectName("chatbot_label")
    scroll_layout.addWidget(chatbot_label)

    self.question_input = QLineEdit()
    self.question_input.setPlaceholderText("Enter your question here.")
    scroll_layout.addWidget(self.question_input)

    self.response_output = QLabel("Phin Response:")
    self.response_output.setObjectName("response_output")
    scroll_layout.addWidget(self.response_output)

    scroll_page.setWidget(scroll_help)
    layout.addWidget(scroll_page)
    self.setLayout(layout)

    self.question_input.returnPressed.connect(self.chatbot_question_answer)

  #Add custom FAQ
  def add_faq_label(self, layout, question, answer):
    question_button = QPushButton(question)
    question_button.setCheckable(True)
    
    answer_label = QLabel(answer)
    answer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    answer_label.setWordWrap(True)
    answer_label.setVisible(False)
    
    question_button.clicked.connect(lambda: answer_label.setVisible(not answer_label.isVisible()))
    layout.addWidget(question_button, alignment=Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(answer_label, alignment=Qt.AlignmentFlag.AlignCenter)

  #Takes in user's input and calls chatbot function for output
  def chatbot_question_answer(self):
    input = self.question_input.text()
    answer = chatbot(input)
    self.response_output.setWordWrap(True)
    self.response_output.setText(f"Phin: {answer}")
    self.clear_inputs()

  #Clears input box after user enters their question
  def clear_inputs(self):
    self.question_input.clear()

#Intelligent chatbot matches common keywords with answers
def chatbot(input):
  input = input.lower()
  responses = {
    "hello": "Hello! How can I assist you today?",
    "hi": "Hello! How can I assist you today?",
    "transaction": "What would you like to know about transactions? We provide features for you to add, remove, and edit your transactions.",
    "transactions": "What would you like to know about transactions? We provide features for you to add, remove, and edit your transactions.",
    "add": "To add a transaction, go to the Transactions page, enter the transaction's information, and click 'Add New Transaction'.",
    "remove": "To remove a transaction, simply click on the transaction you want to remove, and click 'Remove Transaction'.",
    "delete": "To remove a transaction, simply click on the transaction you want to remove, and click 'Remove Transaction'.",
    "edit": "To edit a transaction, click on the transaction you want to edit, edit the information, and click 'Save Changes'.",
    "search": "To search for a transaction, use the search bar on the Transactions page. You can search by date, time, amount, category, or description.",
    "filter": "You can filter transactions by their type (Deposit or Withdrawal).",
    "balance": "Your current balance is displayed in the Home Page.",
    "report": "You can view detailed reports in the Reports page. Just simply select the desired date range.",
    "summary": "You can view detailed summaries in the Reports page. Just simply select the desired date range.",
    "save money": "You can save money by starting with tracking your expenses, cutting unnecessary spending, and setting savings goals. These changes will add up!",
    "help": "I can assist with transactions, balance inquiries, and reports. What do you need help with?",
    "thanks": "You're welcome! Let me know if there's anything else I can do for you. :)",
    "thank you": "You're welcome! Let me know if there's anything else I can do for you. :)",
    "exit": "Goodbye! Feel free to ask me anything financial anytime.",
    "bye": "Goodbye! Feel free to ask me anything financial anytime."
  }
  for keyword, response in responses.items():
    if keyword in input:
      return response
  return "I'm sorry, I didn't understand that. :( Try asking about transactions, balance, or reports."