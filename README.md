# PhinTrack

## Overview
PhinTrack is a secure, cross-platform desktop application that helps students manage their finances. Built with Python and PyQt6, PhinTrack provides financial tracking without an internet connection or sensitive data sharing.

## Features

### Security
* One account per email
* SHA-256 password hashing
* Security question recovery
* Verified malware-free (Windows Defender scan on 03/26/2025)

### Transaction Management
* Log income and expenses with custom categories
* Auto-sorted transaction table by date/time
* Add, edit, or remove transactions

### Visual Reports
* Generate graphs/charts for any period: weekly, monthly, biannually, yearly
* Line graph of cash flow
* Pie charts for income and expense breakdowns
* Custom date range support

### Help Center
* FAQ database with expandable answers
* Fully offline built-in keyword recognition-based/rule-based interactive chatbot for instant guidance

### Validation
* All user inputs validated (email, date, time, amounts)
* Overdraft protection
* Tested on Windows 11 and MacOS Sequoia

### Local Storage
* Data is saved locally onto your computer through CSV files
* All data stays on your device (no cloud storage)

### Real-Time Updates
* Instant income, expense, and balance recalculations
* Auto-refreshing reports

## Libraries & Tools
* Python 3.13
* PyQt6
* hashlib
* csv
* os

## Setup
### Prerequisites
* Python 3.9+
* PyQt6
### Installation
1. Clone repository
git clone https://github.com/leolhcc/PhinTrack.git
cd PhinTrack
2. Install Python packages
pip install -r requirements.txt
3. Launch PhinTrack
python src/main.py

## File Overview
### main.py
PhinTrack entry point - launches the application, manages navigation between pages
### Core Logic
Account.py: Manages user account, password security, and transaction validation
Transaction.py: Stores transaction/financial record data
Report.py: Analyzes transactions and generates income and expense insights
### User Interface
Login_Page.py: User authentication via email and password
Create_Account_Page.py: Account setup
Forgot_Password_Page.py: Resets passwords via security questions
Home_Page.py: Displays dashboard with overall balance, recent transactions, and a financial tip
Transactions_Page.py: Interface for adding, editing, and deleting transactions
Report_Page.py: Visualizes income and expense patterns with line graphs and pie charts
Help_Page.py: Provides answers to FAQs and chatbot assistance
### Data Files
accounts.csv: Stores encrypted credentials of all registered accounts
transactions_{email}.csv: Stores transaction history for each user

## Attributions
### Finance Tips:
* California DFPI: https://dfpi.ca.gov/wp-content/uploads/sites/337/2019/06/8_Tips_for_Financial_Success.pdf
* American Bankers Association: https://www.aba.com/advocacy/community-programs/consumer-resources/kids-money/10-tips-for-college-students 
* NASFAA: https://www.nasfaa.org/10_tips_for_financial_literacy_month 
