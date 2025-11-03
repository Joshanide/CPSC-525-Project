#CPSC 525 Final Project F25
#CWE 259 Hard-coded passwords
#Banking Application

import json
import os
from datetime import datetime
from typing import Dict, Optional

# ============================================================================
# DATA STORAGE CLASS
# ============================================================================
class BankDatabase:
    """Handles all data persistence for the banking system."""
    
    def __init__(self, filename='bank_data.json'):
        self.filename = filename
        self.data = self._load_data()
    
    def _load_data(self) -> Dict:
        """Load bank data from JSON file or create new structure."""
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                return json.load(f)
        else:
            # Initialize default structure
            return {
                'users': {},
                'admin': {'username': 'admin', 'password': 'admin123'},
                'next_account_number': 1000
            }
    
    def save_data(self):
        """Save current data to JSON file."""
        with open(self.filename, 'w') as f:
            json.dump(self.data, f, indent=4)
    
    def get_users(self) -> Dict:
        """Return all user accounts."""
        return self.data['users']
    
    def get_admin_credentials(self) -> Dict:
        """Return admin credentials."""
        return self.data['admin']
    
    def get_next_account_number(self) -> int:
        """Get and increment the next account number."""
        account_num = self.data['next_account_number']
        self.data['next_account_number'] += 1
        return account_num


# ============================================================================
# ACCOUNT CLASS
# ============================================================================
class Account:
    """Represents a single bank account with transaction capabilities."""
    
    def __init__(self, account_number: int, username: str, password: str, 
                 balance: float = 0.0, transaction_history: list = None):
        self.account_number = account_number
        self.username = username
        self.password = password
        self.balance = balance
        self.transaction_history = transaction_history if transaction_history else []
    
    def deposit(self, amount: float) -> bool:
        """Add funds to the account."""
        if amount <= 0:
            print("❌ Deposit amount must be positive.")
            return False
        
        self.balance += amount
        self._add_transaction('DEPOSIT', amount)
        print(f"✅ Successfully deposited ${amount:.2f}")
        print(f"💰 New balance: ${self.balance:.2f}")
        return True
    
    def withdraw(self, amount: float) -> bool:
        """Remove funds from the account."""
        if amount <= 0:
            print("❌ Withdrawal amount must be positive.")
            return False
        
        if amount > self.balance:
            print("❌ Insufficient funds.")
            return False
        
        self.balance -= amount
        self._add_transaction('WITHDRAWAL', amount)
        print(f"✅ Successfully withdrew ${amount:.2f}")
        print(f"💰 New balance: ${self.balance:.2f}")
        return True
    
    def transfer(self, recipient: 'Account', amount: float) -> bool:
        """Transfer funds to another account (e-transfer)."""
        if amount <= 0:
            print("❌ Transfer amount must be positive.")
            return False
        
        if amount > self.balance:
            print("❌ Insufficient funds for transfer.")
            return False
        
        self.balance -= amount
        recipient.balance += amount
        
        self._add_transaction('TRANSFER OUT', amount, 
                             f"To Account #{recipient.account_number}")
        recipient._add_transaction('TRANSFER IN', amount, 
                                   f"From Account #{self.account_number}")
        
        print(f"✅ Successfully transferred ${amount:.2f} to Account #{recipient.account_number}")
        print(f"💰 New balance: ${self.balance:.2f}")
        return True
    
    def _add_transaction(self, transaction_type: str, amount: float, 
                        note: str = ""):
        """Add a transaction to the account history."""
        transaction = {
            'type': transaction_type,
            'amount': amount,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'note': note
        }
        self.transaction_history.append(transaction)
    
    def show_transaction_history(self):
        """Display all transactions for this account."""
        if not self.transaction_history:
            print("\n📋 No transaction history available.")
            return
        
        print("\n" + "="*60)
        print("📋 TRANSACTION HISTORY")
        print("="*60)
        for i, trans in enumerate(self.transaction_history, 1):
            print(f"\n{i}. {trans['type']}")
            print(f"   Amount: ${trans['amount']:.2f}")
            print(f"   Date: {trans['timestamp']}")
            if trans['note']:
                print(f"   Note: {trans['note']}")
        print("="*60)
    
    def to_dict(self) -> Dict:
        """Convert account to dictionary for storage."""
        return {
            'account_number': self.account_number,
            'username': self.username,
            'password': self.password,
            'balance': self.balance,
            'transaction_history': self.transaction_history
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'Account':
        """Create account from dictionary."""
        return Account(
            account_number=data['account_number'],
            username=data['username'],
            password=data['password'],
            balance=data['balance'],
            transaction_history=data['transaction_history']
        )


# ============================================================================
# BANKING SYSTEM CLASS
# ============================================================================
class BankingSystem:
    """Main banking system that manages all operations."""
    
    def __init__(self):
        self.database = BankDatabase()
        self.current_user: Optional[Account] = None
    
    def create_account(self) -> bool:
        """Create a new user account."""
        print("\n" + "="*60)
        print("📝 CREATE NEW ACCOUNT")
        print("="*60)
        
        username = input("Enter username: ").strip()
        
        # Check if username already exists
        users = self.database.get_users()
        if username in users:
            print("❌ Username already exists. Please choose another.")
            return False
        
        password = input("Enter password: ").strip()
        confirm_password = input("Confirm password: ").strip()
        
        if password != confirm_password:
            print("❌ Passwords do not match.")
            return False
        
        # Create new account
        account_number = self.database.get_next_account_number()
        new_account = Account(account_number, username, password)
        
        # Save to database
        users[username] = new_account.to_dict()
        self.database.save_data()
        
        print(f"\n✅ Account created successfully!")
        print(f"🔢 Your account number is: {account_number}")
        print(f"👤 Username: {username}")
        return True
    
    def login(self) -> bool:
        """Login to an existing user account."""
        print("\n" + "="*60)
        print("🔐 USER LOGIN")
        print("="*60)
        
        username = input("Enter username: ").strip()
        password = input("Enter password: ").strip()
        
        users = self.database.get_users()
        
        if username not in users:
            print("❌ Invalid username or password.")
            return False
        
        user_data = users[username]
        if user_data['password'] != password:
            print("❌ Invalid username or password.")
            return False
        
        self.current_user = Account.from_dict(user_data)
        print(f"\n✅ Welcome back, {username}!")
        return True
    
    def admin_login(self) -> bool:
        """Login as admin to view all accounts."""
        print("\n" + "="*60)
        print("👑 ADMIN LOGIN")
        print("="*60)
        
        username = input("Enter admin username: ").strip()
        password = input("Enter admin password: ").strip()
        
        admin = self.database.get_admin_credentials()
        
        if username == admin['username'] and password == admin['password']:
            print("\n✅ Admin access granted!")
            return True
        else:
            print("❌ Invalid admin credentials.")
            return False
    
    def user_menu(self):
        """Display and handle user menu options."""
        while True:
            print("\n" + "="*60)
            print(f"👤 USER MENU - Account #{self.current_user.account_number}")
            print(f"💰 Current Balance: ${self.current_user.balance:.2f}")
            print("="*60)
            print("1. Deposit")
            print("2. Withdraw")
            print("3. E-Transfer")
            print("4. View Transaction History")
            print("5. Logout")
            print("="*60)
            
            choice = input("Enter your choice (1-5): ").strip()
            
            if choice == '1':
                self._handle_deposit()
            elif choice == '2':
                self._handle_withdrawal()
            elif choice == '3':
                self._handle_transfer()
            elif choice == '4':
                self.current_user.show_transaction_history()
            elif choice == '5':
                self._logout()
                break
            else:
                print("❌ Invalid choice. Please try again.")
    
    def _handle_deposit(self):
        """Handle deposit transaction."""
        try:
            amount = float(input("\nEnter deposit amount: $"))
            self.current_user.deposit(amount)
            self._save_current_user()
        except ValueError:
            print("❌ Invalid amount. Please enter a number.")
    
    def _handle_withdrawal(self):
        """Handle withdrawal transaction."""
        try:
            amount = float(input("\nEnter withdrawal amount: $"))
            if self.current_user.withdraw(amount):
                self._save_current_user()
        except ValueError:
            print("❌ Invalid amount. Please enter a number.")
    
    def _handle_transfer(self):
        """Handle e-transfer transaction."""
        try:
            recipient_number = int(input("\nEnter recipient account number: "))
            
            # Find recipient account
            recipient_account = None
            users = self.database.get_users()
            
            for username, user_data in users.items():
                if user_data['account_number'] == recipient_number:
                    recipient_account = Account.from_dict(user_data)
                    break
            
            if not recipient_account:
                print("❌ Recipient account not found.")
                return
            
            if recipient_account.account_number == self.current_user.account_number:
                print("❌ Cannot transfer to your own account.")
                return
            
            amount = float(input("Enter transfer amount: $"))
            
            if self.current_user.transfer(recipient_account, amount):
                # Save both accounts
                users[self.current_user.username] = self.current_user.to_dict()
                users[recipient_account.username] = recipient_account.to_dict()
                self.database.save_data()
                
        except ValueError:
            print("❌ Invalid input. Please enter valid numbers.")
    
    def _save_current_user(self):
        """Save current user data to database."""
        users = self.database.get_users()
        users[self.current_user.username] = self.current_user.to_dict()
        self.database.save_data()
    
    def _logout(self):
        """Logout current user."""
        self._save_current_user()
        print(f"\n👋 Goodbye, {self.current_user.username}!")
        self.current_user = None
    
    def admin_menu(self):
        """Display and handle admin menu options."""
        while True:
            print("\n" + "="*60)
            print("👑 ADMIN MENU")
            print("="*60)
            print("1. View All Accounts")
            print("2. View Specific Account Details")
            print("3. Logout")
            print("="*60)
            
            choice = input("Enter your choice (1-3): ").strip()
            
            if choice == '1':
                self._view_all_accounts()
            elif choice == '2':
                self._view_account_details()
            elif choice == '3':
                print("\n👋 Admin logged out.")
                break
            else:
                print("❌ Invalid choice. Please try again.")
    
    def _view_all_accounts(self):
        """Display all user accounts (admin only)."""
        users = self.database.get_users()
        
        if not users:
            print("\n📋 No accounts in the system.")
            return
        
        print("\n" + "="*60)
        print("📋 ALL ACCOUNTS")
        print("="*60)
        
        for username, user_data in users.items():
            print(f"\n👤 Username: {username}")
            print(f"🔢 Account Number: {user_data['account_number']}")
            print(f"💰 Balance: ${user_data['balance']:.2f}")
            print(f"📊 Transactions: {len(user_data['transaction_history'])}")
            print("-" * 60)
    
    def _view_account_details(self):
        """View detailed information for a specific account (admin only)."""
        try:
            account_num = int(input("\nEnter account number: "))
            users = self.database.get_users()
            
            for username, user_data in users.items():
                if user_data['account_number'] == account_num:
                    account = Account.from_dict(user_data)
                    print(f"\n👤 Username: {username}")
                    print(f"🔢 Account Number: {account_num}")
                    print(f"💰 Balance: ${account.balance:.2f}")
                    account.show_transaction_history()
                    return
            
            print("❌ Account not found.")
        except ValueError:
            print("❌ Invalid account number.")


# ============================================================================
# MAIN APPLICATION
# ============================================================================
def main():
    """Main application entry point."""
    bank = BankingSystem()
    
    print("="*60)
    print("🏦 WELCOME TO OUR BANKING SYSTEM")
    print("="*60)
    
    while True:
        print("\n" + "="*60)
        print("MAIN MENU")
        print("="*60)
        print("1. Create Account")
        print("2. User Login")
        print("3. Admin Login")
        print("4. Exit")
        print("="*60)
        
        choice = input("Enter your choice (1-4): ").strip()
        
        if choice == '1':
            bank.create_account()
        elif choice == '2':
            if bank.login():
                bank.user_menu()
        elif choice == '3':
            if bank.admin_login():
                bank.admin_menu()
        elif choice == '4':
            print("\n👋 Thank you for using our Banking System!")
            break
        else:
            print("❌ Invalid choice. Please try again.")


if __name__ == "__main__":
    main()