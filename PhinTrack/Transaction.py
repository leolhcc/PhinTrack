class Transaction:
  def __init__(self, date, time, type, amount, category, account, description="N/A"):
    self.date = date
    self.time = time
    self.account = account
    self.amount = float(amount)
    if type.lower() == "deposit":
      self.deposit = True
    elif type.lower() == "withdraw":
      self.deposit = False
    else:
      print("Invalid transaction type")
      return
    self.category = category
    self.description = description

  def __eq__(self, other):
    return (
      self.date == other.date and
      self.time == other.time and
      self.deposit == other.deposit and
      self.amount == other.amount and
      self.category == other.category and
      self.description == other.description and
      self.account.email == other.account.email
    )
  
  def __hash__(self):
    return hash((self.date, self.time, self.deposit, self.amount, self.category, self.description, self.account.email))

  #Get & Set methods for Transaction class
  def get_date(self):
    return self.date

  def get_time(self):
    return self.time

  #If it's a deposit, amount will store normally. If it's a withdrawal, the opposite amount will be stored
  def get_type(self):
    if self.deposit:
      return 1
    else:
      return -1
    
  def get_amount(self):
    return self.amount

  def get_category(self):
    return self.category

  def get_description(self):
    return self.description

  def get_account(self):
    return self.account