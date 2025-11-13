# CPSC 525 Final Project F25  
# CWE-259: Hard-Coded Passwords — Banking System & Exploit

# Project Overview
This project demonstrates a 'hard-coded password' security vulnerability through a fully interactive
text-based banking system and a corresponding exploit script that reveals sensitive information.

---

# Banking System (`bank.py`)
- Simulates a realistic banking environment with the following features:
  - User Account Management
      - Create new user accounts with unique usernames and passwords
      - Login system with credential validation
      - User's data is stored in a JSON file (bank_data.json) that is created once a user is created
  - Main Standard Banking Operations
      - Deposit and withdraw funds
      - E-transfer money to other users
      - View your transaction history
  - Investement Games (gambling as its the most secure way to invest)
      - Slots
      - Blackjack
      - Roulette
      - Baccarat
  - Savings Goal Tracker
      - Set a personal savings goal
      - View progress and get notified when goal is reached
      - Option to delete or update the goal at any time
  - Admin Access
      - Login using hard-coded credentials (username: admin, password: admin123)
      - View all user accounts (balances and transactions)
      - View a specific accounts information (balance)
- Contains the hard-coded admin credentials (`username: admin`, `password: admin123`)

# Exploit Script (`bankexploit.py`)
- Demonstrates how an attacker could extract sensitive information:
  - First tries to open `bank.py` and scan it for hard-coded credentials
  - If direct file reading fails, attempts shell-based scanning using grep

---

# How to Run and Use the Banking System (`bank.py`)
1. Open a terminal and navigate to the project directory
3. Type 'python bank.py' to start the application
4. Once the application boots up, first create a user, and then log in as this user
5. Once loggged in you can play around with all the options (for the E-Transfer option you must first create another user to E-Transfer to)

# How to Run the Exploit Script (`bankexploit.py`)
1. Open a terminal and navigate to the project directory
2. Type 'python bankexploit.py' to run the script
3. If the direct file reading succeeds, in the output terminal you will see a big list of lines from `bank.py` that contain either the string "username"
   or "password"
4. Observe this output to locate the admins username and password
5. If the direct file reading fails, in the output terminal you will see one block of lines from `bank.py` that contain the string "username" and
   another block of lines from `bank.py` that contain the string "password"
6. Observe this output to locate the admins username and password