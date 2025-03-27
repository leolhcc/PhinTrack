from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QScrollArea, QLabel, QLineEdit, QMessageBox
from PyQt6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis, QDateTimeAxis, QPieSeries
from PyQt6.QtCore import Qt, QDateTime
from PyQt6.QtGui import QPainter
from Report import Report
from Transaction import Transaction
from datetime import datetime
import csv

class Report_Page(QWidget):
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
                font-weight: bold;
                margin-top: 0px;
                margin-bottom: 0px;
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
                min-width: 800px;
            }
            QPushButton:hover {
                background-color: #44576D;
            }
            #income_label {
                margin-left: 100px;
                color: #247A20;
            }
            #expenses_label {
                margin-right: 100px;
                color: #C22727;
            }
            #generate_report_button {
                max-width: 400px;
            }
            #custom_end_date {
                min-width: 175px;
                max-width: 175px;
            }
            #custom_start_date {
                min-width: 175px;
                max-width: 175px;
            }    
        """)

        self.period = None
        self.custom_start = None
        self.custom_end = None
        self.report = None
        self.setup_layout()

    def setup_layout(self):
        layout = QVBoxLayout()
        scroll_page = QScrollArea()
        scroll_page.setWidgetResizable(True)
        scroll_reports = QWidget()
        scroll_layout = QVBoxLayout(scroll_reports)
        
        #User chooses the time period of the summary
        self.weekly_button = QPushButton("Weekly Report")
        self.weekly_button.clicked.connect(lambda: self.plot_report("weekly"))
        scroll_layout.addWidget(self.weekly_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.monthly_button = QPushButton("Monthly Report")
        self.monthly_button.clicked.connect(lambda: self.plot_report("monthly"))
        scroll_layout.addWidget(self.monthly_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.six_months_button = QPushButton("6 Months Report")
        self.six_months_button.clicked.connect(lambda: self.plot_report("6months"))
        scroll_layout.addWidget(self.six_months_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.yearly_button = QPushButton("Yearly Report")
        self.yearly_button.clicked.connect(lambda: self.plot_report("yearly"))
        scroll_layout.addWidget(self.yearly_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.custom_period_button = QPushButton("Custom Period Report")
        self.custom_period_button.clicked.connect(self.show_custom_inputs)
        scroll_layout.addWidget(self.custom_period_button, alignment=Qt.AlignmentFlag.AlignCenter)

        custom_date_layout = QHBoxLayout()
        custom_date_layout.addStretch()

        #These are shown only when custom report is clicked
        start_date_layout = QHBoxLayout()
        self.custom_start_date_label = QLabel("Start Date")
        self.custom_start_date_label.setObjectName("custom_start_date_label")
        start_date_layout.addWidget(self.custom_start_date_label)
        self.custom_start_date_label.setVisible(False)
        self.custom_start_date = QLineEdit()
        self.custom_start_date.setObjectName("custom_start_date")
        self.custom_start_date.setPlaceholderText("MM/DD/YYYY")
        self.custom_start_date.setObjectName("custom_start_date")
        start_date_layout.addWidget(self.custom_start_date)
        self.custom_start_date.setVisible(False)
        custom_date_layout.addLayout(start_date_layout)
        custom_date_layout.addSpacing(40)

        end_date_layout = QHBoxLayout()
        self.custom_end_date_label = QLabel("End Date")
        self.custom_end_date_label.setObjectName("custom_end_date_label")
        end_date_layout.addWidget(self.custom_end_date_label)
        self.custom_end_date_label.setVisible(False)
        self.custom_end_date = QLineEdit()
        self.custom_end_date.setObjectName("custom_end_date")
        self.custom_end_date.setPlaceholderText("MM/DD/YYYY")
        self.custom_end_date.setObjectName("custom_end_date")
        end_date_layout.addWidget(self.custom_end_date)
        self.custom_end_date.setVisible(False)
        scroll_layout.addLayout(custom_date_layout)
        custom_date_layout.addLayout(end_date_layout)
        custom_date_layout.addStretch()
    
        self.generate_report_button = QPushButton("Generate Report")
        self.generate_report_button.setObjectName("generate_report_button")
        self.generate_report_button.clicked.connect(self.plot_custom_report)
        scroll_layout.addWidget(self.generate_report_button, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.generate_report_button.setVisible(False)

        #Summary of Income and Expense (Text)
        income_expenses_layout = QHBoxLayout()
        self.income_label = QLabel("Total Income: $0.00")
        self.income_label.setObjectName("income_label")
        self.income_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        income_expenses_layout.addWidget(self.income_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.expenses_label = QLabel("Total Expenses: $0.00")
        self.expenses_label.setObjectName("expenses_label")
        self.expenses_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        income_expenses_layout.addWidget(self.expenses_label, alignment=Qt.AlignmentFlag.AlignCenter)
        scroll_layout.addLayout(income_expenses_layout)
    
        #Shows the trend of balance over a time period
        balance_graph = QHBoxLayout()
        balance_graph.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        scroll_layout.addLayout(balance_graph)

        #Summary of Income and Expense (Pie Chart)
        self.chart_graph = QChartView()
        self.chart_graph.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.chart_graph.setFixedHeight(400)
        self.chart_graph.setFixedWidth(1000)
        balance_graph.addWidget(self.chart_graph)

        pie_charts = QHBoxLayout()
        pie_charts.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.income_pie = QChartView()
        self.income_pie.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.income_pie.setFixedHeight(300)
        self.income_pie.setFixedWidth(500)
        pie_charts.addWidget(self.income_pie)

        self.expense_pie = QChartView()
        self.expense_pie.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.expense_pie.setFixedHeight(300)
        self.expense_pie.setFixedWidth(500)
        pie_charts.addWidget(self.expense_pie)

        scroll_layout.addLayout(pie_charts)
        scroll_page.setWidget(scroll_reports)
        layout.addWidget(scroll_page)
        self.setLayout(layout)

    def set_account(self, account):
        self.report = Report(account)

    def is_valid_date(self, date_string):
        try:
            date = datetime.strptime(date_string, "%m/%d/%Y")
            if not (2000 <= date.year <= 2025):
                return False
            cutoff_date = datetime.now().date()
            if date.date() > cutoff_date:
                return False
            return True 
        except ValueError:
            return False
        
    #Inputs for the custom time period graph
    def show_custom_inputs(self):
        self.custom_start_date_label.setVisible(True)
        self.custom_start_date.setVisible(True)
        self.custom_end_date_label.setVisible(True)
        self.custom_end_date.setVisible(True)
        self.generate_report_button.setVisible(True)

    def plot_custom_report(self):
        start_date = self.custom_start_date.text()
        end_date = self.custom_end_date.text()

        if not self.is_valid_date(start_date):
            QMessageBox.warning(self, "Invalid Date", "Start date must be in the format MM/DD/YYYY.")
            return
        if not self.is_valid_date(end_date):
            QMessageBox.warning(self, "Invalid Date", "End date must be in the format MM/DD/YYYY.")
            return
        self.plot_report("custom", start_date, end_date)

    #Plot the balance report based on the selected period (weekly, monthly, 6 months, yearly, custom)
    def plot_report(self, period, start_date=None, end_date=None):
        self.period = period
        if period == "custom":
            self.custom_start = start_date
            self.custom_end = end_date
        else:
            self.custom_start = None
            self.custom_end = None
        if self.main_window.account is None:
            print("No account data available.")
            QMessageBox.warning(self, "Error", "No account data available.")
            return

        #Save all the transactions history of current account into a separate list
        user_email = self.main_window.current_user["email"] if self.main_window.is_logged_in else ""
        filename = f"transactions_{user_email}.csv"
        transactions = []
        try:
            with open(filename, "r") as file:
                reader = csv.reader(file)
                next(reader)  
                for row in reader:
                    if row and row[0] == user_email:
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
            QMessageBox.warning(self, "Error", "No transactions file found.")
            return

        self.main_window.account.transactions = transactions
        self.report = Report(self.main_window.account)

        #Use the filtering function from Report class to get the transactions within the give time period
        filtered_transactions = self.report.filter_transactions_period(period, start_date, end_date)
        if not filtered_transactions:
            QMessageBox.warning(self, "No Data", f"No transactions found for the {period} period.")
            return

        #Filter transactions based on the selected time period
        filtered_transactions.sort(key=lambda t: (self.report.date_tuple(t.get_date()), tuple(map(int, t.get_time().split(":")))))

        all_transactions = self.main_window.account.get_transactions() 
        start_date_tuple = self.report.date_tuple(filtered_transactions[0].get_date()) 
        starting_balance = 0

        #Calculate the starting balance before the first transaction in the filtered period
        for t in all_transactions:
            transaction_date_tuple = self.report.date_tuple(t.get_date())
            if transaction_date_tuple < start_date_tuple:
                if t.get_type() == 1:
                    starting_balance += t.get_amount()
                else:
                    starting_balance -= t.get_amount()

        balance = starting_balance
        min_balance = balance
        max_balance = balance
        series = QLineSeries()

        #Start plotting with the first transaction date
        fst_date = QDateTime.fromString(filtered_transactions[0].get_date(), "MM/dd/yyyy")
        series.append(fst_date.toMSecsSinceEpoch(), balance)

        #If only one transaction exists, add another later point just for visualization purpose
        if len(filtered_transactions) == 1:
            t = filtered_transactions[0]
            if t.get_type() == 1:
                balance += t.get_amount()
            else:
                balance -= t.get_amount()
            
            ltr_date = fst_date.addSecs(3600)
            series.append(ltr_date.toMSecsSinceEpoch(), balance)
            
            min_balance = min(min_balance, balance)
            max_balance = max(max_balance, balance)
        else:
            #Iterate through filtered transactions, updating balance and adding points to the graph
            for t in filtered_transactions:
                date_str = t.get_date()
                time_str = t.get_time()
                date = QDateTime.fromString(date_str, "MM/dd/yyyy")
                
                hours, minutes = map(int, time_str.split(":"))
                date = date.addSecs(hours * 3600 + minutes * 60)
                
                #Update balance each time and add it to the graph series
                if t.get_type() == 1:
                    balance += t.get_amount()
                else:
                    balance -= t.get_amount()
                
                min_balance = min(min_balance, balance)
                max_balance = max(max_balance, balance)
                series.append(date.toMSecsSinceEpoch(), balance)

        #Set Header and Axis title for each period's graph
        if period == "weekly":
            graph_title = "Account Balance Over the Past Week"
            income_title = "Income Summary for the Past Week"
            expense_title = "Expense Breakdown for the Past Week"
        elif period == "monthly":
            graph_title = "Account Balance Over the Past Month"
            income_title = "Income Summary for the Past Month"
            expense_title = "Expense Breakdown for the Past Month"
        elif period == "6months":
            graph_title = "Account Balance Over the Past 6 Months"
            income_title = "Income Summary for the Past 6 Months"
            expense_title = "Expense Breakdown for the Past 6 Months"
        elif period == "yearly":
            graph_title = "Account Balance Over the Past Year"
            income_title = "Income Summary for the Past Year"
            expense_title = "Expense Breakdown for the Past Year"
        elif period == "custom":
            graph_title = f"Account Balance from {start_date} to {end_date}"
            income_title = f"Income Summary from {start_date} to {end_date}"
            expense_title = f"Expense Breakdown from {start_date} to {end_date}"
        else:
            graph_title = "Account Balance Over Time"
            income_title = "Income Summary"
            expense_title = "Expense Breakdown"

        # Create and configure the balance trend chart
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle(graph_title)
        chart.legend().hide()

        #x-axis (date)
        axis_x = QDateTimeAxis()
        axis_x.setFormat("MM/dd/yyyy")
        axis_x.setTitleText("Date")
        axis_x.setTickCount(2)
        start_date = QDateTime.fromString(filtered_transactions[0].get_date(), "MM/dd/yyyy")
        end_date = QDateTime.fromString(filtered_transactions[-1].get_date(), "MM/dd/yyyy")
        axis_x.setRange(start_date, end_date)
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_x)

        #y-axis (balance)
        axis_y = QValueAxis()
        axis_y.setTitleText("Balance ($)")
        axis_y.setLabelFormat("%.2f")
        axis_y.setRange(min_balance, max_balance)
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)

        #Display summaries as text
        (total_income, total_spending, total_balance, income_by_category, expense_by_category, _, _) = self.report.generate_summary(filtered_transactions)
        self.income_label.setText(f"Total Deposits: ${total_income:.2f}")
        self.expenses_label.setText(f"Total Expenses: ${total_spending:.2f}")

        #Create income and expense pie charts
        income_pie_chart = QChart()
        income_series = QPieSeries()
        for category, amount in income_by_category.items():
            income_series.append(f"{category} (${amount:.2f})", amount)
        income_pie_chart.addSeries(income_series)
        income_pie_chart.setTitle(income_title)
        income_pie_chart.legend().setAlignment(Qt.AlignmentFlag.AlignRight)

        expense_pie_chart = QChart()
        expense_series = QPieSeries()
        for category, amount in expense_by_category.items():
            expense_series.append(f"{category} (${amount:.2f})", amount)
        expense_pie_chart.addSeries(expense_series)
        expense_pie_chart.setTitle(expense_title)
        expense_pie_chart.legend().setAlignment(Qt.AlignmentFlag.AlignRight)

        #Display the charts in User Interface
        self.chart_graph.setChart(chart)
        self.income_pie.setChart(income_pie_chart)
        self.expense_pie.setChart(expense_pie_chart)

        print(f"Successfully plotted report for {period} period with {len(filtered_transactions)} transactions")

    def update_reports(self):
        if self.period:
            if self.period == "custom" and self.custom_start and self.custom_end:
                self.plot_report("custom", self.custom_start, self.custom_end)
            else:
                self.plot_report(self.period)

    def clear_reports(self):
        self.custom_start_date.clear()
        self.custom_end_date.clear()

        self.custom_start_date_label.setVisible(False)
        self.custom_start_date.setVisible(False)
        self.custom_end_date_label.setVisible(False)
        self.custom_end_date.setVisible(False)
        self.generate_report_button.setVisible(False)

        cleared_chart = QChart()
        cleared_chart.setTitle("Account Balance Over Time")
        self.chart_graph.setChart(cleared_chart)

        income_pie = QChart()
        income_pie.setTitle("Income Summary")
        self.income_pie.setChart(income_pie)

        expense_pie = QChart()
        expense_pie.setTitle("Expense Breakdown")
        self.expense_pie.setChart(expense_pie)

        self.income_label.setText("Total Income: $0.00")
        self.expenses_label.setText("Total Expenses: $0.00")

        self.period = None
        self.custom_start = None
        self.custom_end = None