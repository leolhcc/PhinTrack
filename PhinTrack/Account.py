from Transaction import Transaction
import csv
import hashlib
from datetime import datetime

#Data storage for all accounts and transactions (used to export to CSV)
emails = set()
accounts = []
existing_transactions = []
      
class Account:
  def __init__(self, username, email, password, security_question, security_answer, init_balance):
    self.username = username
    self.email = email
    self.password = hashlib.sha256(password.encode()).hexdigest()
    self.security_question = security_question
    self.security_answer = security_answer
    self.balance = float(init_balance)
    self.transactions = []
    if email not in emails:
      self.email = email
      emails.add(email)
      if not any(acc.email == self.email for acc in accounts):
        accounts.append(self)
      account_to_csv()  #Save new account to CSV
    else:
      print("This email already exists.")

  def __eq__(self, other):
    if self.username == other.username and self.email == other.email and self.password == other.password and self.security_question == other.security_question and self.security_answer == other.security_answer and self.balance == other.balance:
      return True
    else:
      return False

  def __hash__(self):
    return hash((self.username, self.email, self.password, self.security_question, self.security_answer, self.balance))

#Check for validation when adding/removing/editing transactions by iterating an ordered copy of account's transactions
  def can_remove_deposit(self, old_transaction):
    transactions = self.transactions
    transactions_copy = sorted(transactions, key=lambda t: (t.date, t.time))
    transactions_copy.remove(old_transaction)  #Simulate removal of old transaction
    transactions_copy = sorted(transactions_copy, key=lambda t: (t.date, t.time))

    #Iterate through new transactions
    current_balance = 0
    for transaction in transactions_copy:
      current_balance += transaction.get_amount() * transaction.get_type()
      if current_balance < 0:  #Remove deposit is invalid if at any point the balance is < 0
        return False
      
    if current_balance >= 0:
      return True
  
  def can_add_withdrawal(self, new_transaction):
    transactions = self.transactions
    transactions_copy = sorted(transactions, key=lambda t: (t.date, t.time))
    transactions_copy.append(new_transaction)  #Simulate adding new transaction
    transactions_copy = sorted(transactions_copy, key=lambda t: (t.date, t.time))

    current_balance = 0
    for transaction in transactions_copy:
      current_balance += transaction.get_amount() * transaction.get_type()
      if current_balance < 0:
        return False
      
    if current_balance >= 0:
      return True

  def can_edit(self, old_transaction, new_transaction):
      transactions = self.transactions
      transactions_copy = sorted(transactions, key=lambda t: (t.date, t.time))
      transactions_copy.remove(old_transaction)  #Simulate editing transaction (Removing old + adding new)
      transactions_copy.append(new_transaction)
      transactions_copy = sorted(transactions_copy, key=lambda t: (t.date, t.time))

      current_balance = 0
      for transaction in transactions_copy:
        current_balance += transaction.get_amount() * transaction.get_type()
        if current_balance < 0:
          return False
      
      if current_balance >= 0:
        return True

  def add_transaction(self, t):
    if t.get_type() == -1 and self.balance - t.get_amount() < 0:
        print(f"Transaction failed: Insufficient funds. Current balance is {self.balance}")
        return False  # Prevent transaction if funds are insufficient
    elif t.get_type() == -1:
        self.balance -= t.get_amount()  # Subtract for withdrawals
    else:
        self.balance += t.get_amount()  # Add for deposits

    self.transactions.append(t)  #Update current account's transactions list
    existing_transactions.append(t)  #Update the global transactions list
    account_to_csv()  #Update account's balance in CSV
    export_transactions_to_csv(self)  #Update user-specific transactions file
    print(f"✅ Transaction added: {t}")
    return True

  def remove_transaction(self, t):
    #Remove the transaction from the account's transactions list
    if t in self.transactions:
        self.transactions.remove(t)

    #Remove the transaction from the global existing_transactions list
    if t in existing_transactions:
        existing_transactions.remove(t)

    # Update the account balance
    if t.deposit:
        self.balance -= t.amount
    else:
        self.balance += t.amount 

    account_to_csv()
    export_transactions_to_csv(self)
    print(f"✅ Transaction removed: {t}")

  #Get & Set methods for Account class
  def get_transactions(self):
    return self.transactions
  def get_balance(self):
    return self.balance 
  def update_balance(self, amount):
    self.balance += amount
  def get_username(self):
    return self.username
  def get_email(self):
    return self.email
  def get_password(self):
    return self.password
  def set_password(self, new_password):
    self.password = new_password
  def get_security_question(self): 
    return self.security_question
  def get_security_answer(self):
    return self.security_answer

#Updates when new account is made or the balance of an account changes
def account_to_csv(filename="accounts.csv"):
    updated_accounts = {}

    #Read the existing accounts from CSV and store them in a dictionary
    try:
        with open(filename, "r", newline="") as file:
            reader = csv.reader(file)
            headers = next(reader)  #Skip the header
            for row in reader:
                if len(row) >= 6:
                    email = row[1]
                    updated_accounts[email] = row  # Store existing account data
    except FileNotFoundError:
        print("⚠️ No previous accounts file found. Creating a new one.")

    #Update balances or add new accounts
    for acc in accounts:
      if acc.email in updated_accounts:
        current_balance = updated_accounts[acc.email][5]

        #Update balance if not yet updated
        if current_balance != str(acc.balance):
          updated_accounts[acc.email][5] = str(acc.balance)
          break

      #Add new account if it's not in existing accounts
      else:
        updated_accounts[acc.email] = [
          acc.username, acc.email, acc.password,
          acc.security_question, acc.security_answer, str(acc.balance)
        ]

    #Write all updated accounts back to the CSV
    try:
        with open(filename, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["username", "email", "password", "security_question", "security_answer", "balance"])
            for account_data in updated_accounts.values():
                writer.writerow(account_data)

        print(f"✅ Accounts successfully updated in {filename}")
    except Exception as e:
        print(f"❌ Error saving accounts to CSV: {e}")

#Export all of current user's transactions to their unique CSV files
def export_transactions_to_csv(account, filename=None):
    if not filename:
        filename = f"transactions_{account.email}.csv"  # User-specific file

    try:
        with open(filename, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Account Email", "Date", "Time", "Amount", "Category", "Description"])

            for transaction in existing_transactions:
                if transaction.get_account().email == account.email:  # Only save transactions for this user
                    writer.writerow([
                        transaction.get_account().email,
                        transaction.get_date(),
                        transaction.get_time(),
                        transaction.get_amount() * transaction.get_type(),
                        transaction.get_category(),
                        transaction.get_description(),
                    ])

        print(f"✅ Transactions exported to {filename}")
    except Exception as e:
        print(f"❌ Error exporting transactions to CSV: {e}")

#Prevents accounts' storage list from resetting after the window closes   
def load_accounts_from_csv(filename="accounts.csv"):
  try:
        with open(filename, "r", newline="") as file:
            reader = csv.reader(file)
            next(reader)  
            for row in reader:
                if len(row) == 6: 
                    username, email, password, security_question, security_answer, balance = row
                    if not any(acc.email == email for acc in accounts):
                      accounts.append(Account(username, email, password, security_question, security_answer, float(balance)))
                      print(f"✅ Accounts loaded from {filename}")
  except FileNotFoundError:
    print("⚠️ No previous accounts file found. Starting fresh.")
  except Exception as e:
    print(f"❌ Error loading accounts: {e}")