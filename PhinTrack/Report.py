class Report:
  def __init__(self, account):
    self.account = account

  #Generate a summary (income, expense, balance) of the given transaction
  def generate_summary(self, transactions):
    total_income = 0
    total_expenses = 0
    income_summary = {}
    expense_summary = {}

    #Iterate through the transactions and save each income/expense in separate dictionaries
    for t in transactions:
      category = t.get_category().lower()
      amount = t.get_amount()
      if t.get_type() == 1:
        total_income += amount  #Sum up the total income for later
        if category not in income_summary:
          income_summary[category] = 0  #Create a new category if we haven't already checked it
        income_summary[category] += amount  #Sum up the amount spent for each income category
      else:
        total_expenses += amount
        if category not in expense_summary:
          expense_summary[category] = 0
        expense_summary[category] += amount

    #Percentages used for the pie chart
    income_percentages = {}
    expense_percentages = {}

    #Iterate through each item in the income/expense dictionaries
    for category, amount in income_summary.items():
      income_percentages[category] = (amount / total_income) * 100 if total_income > 0 else 0
    for category in expense_summary:
      expense_percentages[category] = (amount / total_expenses) * 100 if total_expenses > 0 else 0
    total_balance = total_income - total_expenses

    return (total_income, total_expenses, total_balance, income_summary, expense_summary, income_percentages, expense_percentages)

  #Get the specific date that's x days before the most recent transaction date to filter the tranactions within those two dates
  def get_start_date(self, most_recent_date, days_before):
    month, day, year = most_recent_date.split("/")
    month = int(month)
    day = int(day)
    year = int(year)
    while days_before > 0:
      if day > days_before:
        day -= days_before
        days_before = 0
      else:
        days_before -= day
        month -= 1
        if month < 1:
          month = 12
          year -= 1
        day = 30
    return f"{month:02}/{day:02}/{year}"

  #Filter the transactions that are within the start_date and end_date
  def filter_transactions_period(self, period, start_date=None, end_date=None):
    if not self.account:  #No account data is available
      return []
    transactions = self.account.get_transactions()
    if not transactions:  #No transactions in this account
      return []
    if period == "custom" and start_date and end_date:  #Set the start and end dates to the user's custom dates
      start_tuple = self.date_tuple(start_date)
      end_tuple = self.date_tuple(end_date)
    else:
      most_recent_transaction = transactions[0].get_date()
      for t in transactions:
        if self.date_tuple(t.get_date()) > self.date_tuple(most_recent_transaction):
          most_recent_transaction = t.get_date()

      #Set the start and end dates for non-custom reports
      if period == "weekly":
        start_date = self.get_start_date(most_recent_transaction, 7)
      elif period == "monthly":
        start_date = self.get_start_date(most_recent_transaction, 30)
      elif period == "6months":
        start_date = self.get_start_date(most_recent_transaction, 180)
      elif period == "yearly":
        start_date = self.get_start_date(most_recent_transaction, 365)
      else:
        return transactions
      start_tuple = self.date_tuple(start_date)
      end_tuple = self.date_tuple(most_recent_transaction)

    #Filter the transactions within the calculated start_date and end_date period
    filtered_transactions = []
    for t in transactions:
      transaction_date = self.date_tuple(t.get_date())
      if start_tuple <= transaction_date <= end_tuple:
        filtered_transactions.append(t)

    return filtered_transactions

  #Return the date in this format with three separate return values
  def date_tuple(self, date):
    month, day, year = date.split("/")
    return int(year), int(month), int(day)