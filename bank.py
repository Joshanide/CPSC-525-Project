#CPSC 525 Final Project F25
#CWE 259 Hard-coded passwords
#Banking Application

import json
import os
import random
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
             balance: float = 0.0, transaction_history: list = None, savings_goal: float = 0.0):
        self.account_number = account_number
        self.username = username
        self.password = password
        self.balance = balance
        self.transaction_history = transaction_history if transaction_history else []
        self.savings_goal = savings_goal

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
        return {
            'account_number': self.account_number,
            'username': self.username,
            'password': self.password,
            'balance': self.balance,
            'transaction_history': self.transaction_history,
            'savings_goal': self.savings_goal
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'Account':
        return Account(
            account_number=data['account_number'],
            username=data['username'],
            password=data['password'],
            balance=data['balance'],
            transaction_history=data['transaction_history'],
            savings_goal=data.get('savings_goal', 0.0)
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
            print("5. Investing")
            print("6. Savings Goal Menu")
            print("7. Logout")
            print("="*60)
            
            choice = input("Enter your choice (1-7): ").strip()
            
            if choice == '1':
                self._handle_deposit()
            elif choice == '2':
                self._handle_withdrawal()
            elif choice == '3':
                self._handle_transfer()
            elif choice == '4':
                self.current_user.show_transaction_history()
            elif choice == '5':
                self.investmentmenu()
            elif choice == '6':
                self._savings_goal_menu()
            elif choice == '7':
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

    def investmentmenu(self):
        """Display and handle user investment menu options."""

        while True:
            print("\n" + "="*60)
            print("📈 INVESTMENT MENU")
            print(f"💰 Current Balance: ${self.current_user.balance:.2f}")
            print("="*60)
            print("1. Slots")
            print("2. Blackjack")
            print("3. Roulette")
            print("4. Baccarat")
            print("5. Back")
            print("="*60)

            choice = input("Enter your choice (1-5): ").strip()
            
            if choice == '1':
                self._slots()
            elif choice == '2':
                self._blackjack()
            elif choice == '3':
                self._roulette()
            elif choice == '4':
                self._baccarat()
            elif choice == '5':
                break
            else:
                print("❌ Invalid choice. Please try again.")
            
    def _slots(self):
        """Slots game"""

        """Betting menu"""
        print("\n" + "="*60)
        print("🎰 SLOTS")
        print(f"💰 Current Balance: ${self.current_user.balance:.2f}")
        print("="*60)

        """Enter bet and withdraw that money"""
        while True:
            try:
                amount = float(input("\nEnter bet amount: $"))
                if self.current_user.withdraw(amount):
                    self._save_current_user()
                    break
                else:
                    print("Insufficient funds.")
                    return
            except ValueError:
                print("❌ Invalid amount. Please enter a number.")

        """Generate and print the slot roll"""
        symbols = []
        numtosym = ["🍒", "🍋", "🔔", "💎", "7️⃣", "🍉", "⭐", "🍀", "🍇", "💰", "🔥", "🍊"]
        slotprint = ""
        for rows in range(3):
            symbols.append([])
            for columns in range(5):
                value = random.randint(0,11)
                symbols[rows].append(value)
                slotprint += numtosym[value] + " "
            slotprint += "\n"

        print("="*60)
        print(slotprint)

        """Check for win"""
        win = 0
        for x in range(3):
            current = 1
            for y in range(5):
                if x==0:
                    if symbols[0][y] == symbols[1][y] and symbols[0][y] == symbols[2][y]:
                        win += 3
                    if y <= 2:
                        if symbols[0][y] == symbols[1][y+1] and symbols [0][y] == symbols[2][y+2]:
                            win +=3
                    if y >= 2:
                        if symbols[0][y] == symbols[1][y-1] and symbols [0][y] == symbols[2][y-2]:
                            win +=3
                if y > 0:
                    if symbols[x][y] == symbols[x][y-1]:
                        current += 1
                    else:
                        if current > 2:
                            win += current
                        current = 1
            if current > 2:
                win += current
        if win > 0:
            print("Winner!")
            self.current_user.deposit(amount*(win+1))
        else:
            print("Better luck next time.")

    def _blackjack(self):
        """Blackjack game"""

        """Betting menu"""
        print("\n" + "="*60)
        print("🃏 BLACKJACK")
        print(f"💰 Current Balance: ${self.current_user.balance:.2f}")
        print("="*60)

        """Enter bet and withdraw that money"""
        while True:
            try:
                amount = float(input("\nEnter bet amount: $"))
                if self.current_user.withdraw(amount):
                    self._save_current_user()
                    break
                else:
                    print("Insufficient funds.")
                    return
            except ValueError:
                print("❌ Invalid amount. Please enter a number.")

        print("="*60)

        """Create the deck"""
        suits = ['♣️','♠️','♥️','♦️']
        cards = ['A','2','3','4','5','6','7','8','9','10','J','Q','K']
        deck = [(card, suit) for suit in suits for card in cards]

        """Shuffle the deck and deal the cards"""
        random.shuffle(deck)
        player_hand = [deck.pop(), deck.pop()]
        dealer_hand = [deck.pop(), deck.pop()]

        """Player choice/move"""
        while True:
            print("Your hand: ", '  '.join(f"{rank}{suit}" for rank, suit in player_hand))
            print(f"Dealer's hand: ? {dealer_hand[1][0]}{dealer_hand[1][1]}")
            if (cardeval(player_hand)==21):
                print("Blackjack! 🤑")
                self.current_user.deposit(amount+amount*1.5)
                input("\nPress Enter to continue.")
                return
            print("1. Hit")
            print("2. Double")
            print("3. Stand")

            choice = input("Enter your choice (1-3): ").strip()
            print("="*60)
            
            if choice == '1':
                player_hand.append(deck.pop())
                if (cardeval(player_hand) > 21):
                    break
            elif choice == '2':
                amount = amount*2
                player_hand.append(deck.pop())
                break
            elif choice == '3':
                break
            else:
                print("❌ Invalid choice. Please try again.")

        """Scoring"""
        print("Dealer's hand: ", '  '.join(f"{rank}{suit}" for rank, suit in dealer_hand))
        while (cardeval(dealer_hand)<17):
            dealer_hand.append(deck.pop())
            print("Dealer's hand: ", '  '.join(f"{rank}{suit}" for rank, suit in dealer_hand))
        print("Your hand: ", '  '.join(f"{rank}{suit}" for rank, suit in player_hand))

        if (cardeval(player_hand) > 21):
            print("You bust. 😢")
        elif (cardeval(dealer_hand) > 21):
            print("The dealer busts! 🤑")
            self.current_user.deposit(amount*2)
        elif (cardeval(dealer_hand)>cardeval(player_hand)):
            print("The dealer won. 😢")
        elif (cardeval(dealer_hand)==cardeval(player_hand)):
            print("It's a tie! ⚖️")
            self.current_user.deposit(amount)
        else:
            print("You won! 🤑")
            self.current_user.deposit(amount*2)

        input("\nPress Enter to continue.")
    
    def _roulette(self):
        """Roulette game"""

        """Betting menu"""
        print("\n" + "="*60)
        print("🤑 ROULETTE")
        print(f"💰 Current Balance: ${self.current_user.balance:.2f}")
        print("="*60)

        """Enter bet and withdraw that money"""
        while True:
            try:
                amount = float(input("\nEnter bet amount: $"))
                if self.current_user.withdraw(amount):
                    self._save_current_user()
                    break
                else:
                    print("Insufficient funds.")
                    return
            except ValueError:
                print("❌ Invalid amount. Please enter a number.")

        print("""                       | 0🟩 |
        |  1-18  |  🟥1 |  ⬛2 |  🟥3 |
        | 1st 12 |  ⬛4 |  🟥5 |  ⬛6 |
        |  even  |  🟥7 |  ⬛8 |  🟥9 |
                 | ⬛10 | ⬛11 | 🟥12 |
        | 2nd 12 | ⬛13 | 🟥14 | ⬛15 |
        |   red  | 🟥16 | ⬛17 | 🟥18 |
        |  black | 🟥19 | ⬛20 | 🟥21 |
                 | ⬛22 | 🟥23 | ⬛24 |
        |   odd  | 🟥25 | ⬛26 | 🟥27 |
        | 3rd 12 | ⬛28 | ⬛29 | 🟥30 |
        |  19-36 | ⬛31 | 🟥32 | ⬛33 |
                 | 🟥34 | ⬛35 | 🟥36 |
                 | col 1| col 2| col 3|""")
        
        """Roll the ball"""
        ball = random.randint(0,36)
        extras = []
        if ball % 2 == 0:
            extras.append("even")
        else:
            extras.append("odd")
        if ball <= 18:
            extras.append("1-18")
        else:
            extras.append("19-36")
        if ball <= 12:
            extras.append("1st 12")
        elif ball <= 24:
            extras.append("2nd 12")
        else:
            extras.append("3rd 12")
        if ball % 3 == 0:
            extras.append("col 3")
        elif ball % 3 == 1:
            extras.append("col 1")
        else: 
            extras.append("col 2")
        if ball in [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36]:
            extras.append("red")
        elif ball == 0:
            "green"
        else: 
            extras.append("black")

        """Betting and winning"""
        while True:
            choice = input("Enter your choice: ").strip()
            print("="*60)

            if choice not in ['1-18','1st 12','even','2nd 12','red','black','odd','3rd 12','19-36','col 1','col 2','col 3']:
                try:
                    if int(choice)>36 or int(choice)<0:
                        print("❌ Invalid choice. Please try again.")
                    else:
                        print("The ball landed in ",ball)
                        if (ball == int(choice)):
                            print("You win!")
                            self.current_user.deposit(amount*36)
                        else:
                            print("You lose!")
                        break
                except ValueError:
                    print("❌ Invalid choice. Please try again.")
            else:
                print("The ball landed in ",ball)
                if choice in extras:
                    print("You win!")
                    if choice in ['1st 12','2nd 12','3rd 12','col 1','col 2','col 3']:
                        self.current_user.deposit(amount*3)
                    else:
                        self.current_user.deposit(amount*2)
                else:
                    print("You lose!")
                break
        
    def _baccarat(self):
        """Baccarat game"""

        """Betting menu"""
        print("\n" + "="*60)
        print("🃏 BACCARAT")
        print(f"💰 Current Balance: ${self.current_user.balance:.2f}")
        print("="*60)

        """Enter bet and withdraw that money"""
        while True:
            try:
                amount = float(input("\nEnter bet amount: $"))
                if self.current_user.withdraw(amount):
                    self._save_current_user()
                    break
                else:
                    print("Insufficient funds.")
                    return
            except ValueError:
                print("❌ Invalid amount. Please enter a number.")

        while True:
            print("\n1.Player")
            print("2.Banker")
            choice = input("Enter your choice (1-2): ").strip()
            print("="*60)

            if choice not in ['1','2']:
                print("❌ Invalid choice. Please try again.")
            else:
                break

        """Create the deck"""
        suits = ['♣️','♠️','♥️','♦️']
        cards = ['A','2','3','4','5','6','7','8','9','10','J','Q','K']
        deck = [(card, suit) for suit in suits for card in cards]

        """Shuffle the deck and deal the cards"""
        random.shuffle(deck)
        player_hand = [deck.pop(), deck.pop()]
        banker_hand = [deck.pop(), deck.pop()]

        print("\nPlayer's hand: ", '  '.join(f"{rank}{suit}" for rank, suit in player_hand))
        print("Banker's hand: ", '  '.join(f"{rank}{suit}" for rank, suit in banker_hand))
        print("Drawing third cards...")

        """Third card drawing"""
        #if (baccarateval(player_hand) >= 8 or baccarateval(banker_hand) >= 8):
        #    break
        if (baccarateval(player_hand)<=5):
            thirdcard = deck.pop()
            cardscore = baccarateval([thirdcard])
            player_hand.append(thirdcard)
            if (baccarateval(banker_hand)<=2):
                banker_hand.append(deck.pop())
            elif (baccarateval(banker_hand)==3):
                if (cardscore!=8):
                    banker_hand.append(deck.pop())
            elif (baccarateval(banker_hand)==4):
                if (cardscore not in [0,1,8,9]):
                    banker_hand.append(deck.pop())
            elif (baccarateval(banker_hand)==5):
                if (cardscore in [4,5,6,7]):
                    banker_hand.append(deck.pop())
            elif (baccarateval(banker_hand)==6):
                if (cardscore in [6,7]):
                    banker_hand.append(deck.pop())
        else:
            if (baccarateval(banker_hand)<=5):
                player_hand.append(deck.pop())

        print("\nPlayer's hand: ", '  '.join(f"{rank}{suit}" for rank, suit in player_hand))
        print("Banker's hand: ", '  '.join(f"{rank}{suit}" for rank, suit in banker_hand))

        if (baccarateval(player_hand)>baccarateval(banker_hand)):
            print("The Player won.")
            if choice == 1:
                print("You win!")
                self.current_user.deposit(amount*2)
            else:
                print("Better luck next time.")
        elif (baccarateval(player_hand)==baccarateval(banker_hand)):
            print("It's a tie.")
            self.current_user.deposit(amount)
        else:
            print("The Banker won.")
            if choice == 2:
                print("You win!")
                self.current_user.deposit(amount*2)
            else:
                print("Better luck next time.")
            
    def cardeval(hand):
        """Evaluate score of cards in a hand for blackjack"""
        value = 0
        aces = 0
        for card in hand:
            if card[0] in ['J','Q','K']:
                value += 10
            elif card[0] == 'A':
                value += 11
                aces += 1
            else:
                value += int(card[0])
        while value > 21:
            if aces == 0:
                break
            value -= 10
            aces -= 1
        return value

    def baccarateval(hand):
        """Evaluate score of cards in a hand for baccarat"""
        value = 0
        for card in hand:
            if card[0] in ['J','Q','K']:
                value += 10
            elif card[0] == 'A':
                value += 1
            else:
                value += int(card[0])
        return value % 10

    def _savings_goal_menu(self):
        """Savings goal menu and tracking."""
        while True:
            user = self.current_user
            print("\n" + "="*60)
            print("SAVINGS GOAL MENU")
            print("="*60)
            print(f"👤 Username: {user.username}")
            print(f"💰 Current Balance: ${user.balance:.2f}")
            print(f"🎯 Current Savings Goal: ${user.savings_goal:.2f}")

            if user.savings_goal == 0:
                print("⚠️ No savings goal set.")
            elif user.balance >= user.savings_goal:
                print("✅ Congratulations! You've reached your savings goal!")
            else:
                remaining = user.savings_goal - user.balance
                percent = (user.balance / user.savings_goal) * 100
                print(f"Progress: {percent:.2f}% complete")
                print(f"You need ${remaining:.2f} more to reach your goal.")

            print("\nOptions:")
            print("1. Set New Savings Goal")
            print("2. Delete Current Goal")
            print("3. Back")
            print("="*60)

            choice = input("Enter your choice (1-3): ").strip()

            if choice == '1':
                self._set_new_savings_goal()
            elif choice == '2':
                confirm = input("Are you sure you want to delete your savings goal? (y/n): ").strip().lower()
                if confirm == 'y':
                    user.savings_goal = 0.0
                    self._save_current_user()
                    print("🗑️ Savings goal deleted.")
            elif choice == '3':
                break
            else:
                print("❌ Invalid choice. Please try again.")

    def _set_new_savings_goal(self):
        """Prompt user to set a new savings goal."""
        try:
            new_goal = float(input("Enter new savings goal amount: $"))
            if new_goal <= 0:
                print("❌ Goal must be greater than zero.")
                return
            self.current_user.savings_goal = new_goal
            self._save_current_user()
            print(f"✅ New savings goal set: ${new_goal:.2f}")
        except ValueError:
            print("❌ Invalid input. Please enter a numeric value.")

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