import mysql.connector

connection = mysql.connector.connect(host='localhost',
                                     user='root',
                                     password='12345',
                                     database='banking_app')

cursor = connection.cursor()


# function to add a new user to the database
def add_user(account_number, pin, name, email, is_admin=False):
  query = """
        INSERT INTO users (account_number, pin, name, email, is_admin)
        VALUES (%s, %s, %s, %s, %s)
    """
  values = (account_number, pin, name, email, is_admin)
  cursor.execute(query, values)
  connection.commit()


# function to add a new account for a user
def create_account(account_number, initial_balance):
  query = """
        INSERT INTO accounts (account_number, balance)
        VALUES (%s, %s)
    """
  values = (account_number, initial_balance)
  cursor.execute(query, values)
  connection.commit()


# function to check if a user exists in the database
def user_exists(account_number):
  query = """
        SELECT COUNT(*) FROM users WHERE account_number = %s
    """
  values = (account_number, )
  cursor.execute(query, values)
  result = cursor.fetchone()
  if result[0] == 1:
    return True
  else:
    return False


#  function to create a new account for a user
def new_account():
  account_number = int(input("Enter account number: "))
  if user_exists(account_number):
    print("User already exists")
    return
  pin = int(input("Enter PIN: "))
  name = input("Enter name: ")
  email = input("Enter email: ")
  initial_balance = float(input("Enter initial balance: "))
  add_user(account_number, pin, name, email)
  create_account(account_number, initial_balance)
  print("Account created successfully!")


def login(account_number, pin):
  query = """
        SELECT * FROM users WHERE account_number = %s AND pin = %s
    """
  values = (account_number, pin)
  cursor.execute(query, values)
  user = cursor.fetchone()
  if user:
    return user
  else:
    print("Invalid account number or PIN")
    return None


def get_balance(account_number):
  query = """
        SELECT balance FROM accounts WHERE account_number = %s
    """
  values = (account_number, )
  cursor.execute(query, values)
  result = cursor.fetchone()
  if result:
    return float(result[0])
  else:
    return None


def deposit(account_number, amount):
  current_balance = get_balance(account_number)
  if current_balance is None:
    print("Account does not exist")
    return
  new_balance = current_balance + amount
  query = """
        UPDATE accounts SET balance = %s WHERE account_number = %s
    """
  values = (new_balance, account_number)
  cursor.execute(query, values)
  connection.commit()
  print("Deposit successful. New balance: ${:.2f}".format(new_balance))


#  function to withdraw money from an account
def withdraw(account_number, amount):
  current_balance = get_balance(account_number)
  if current_balance is None:
    print("Account does not exist")
    return
  if current_balance < amount:
    print("Insufficient balance")
    return
  new_balance = current_balance - amount
  query = """
        UPDATE accounts SET balance = %s WHERE account_number = %s
    """
  values = (new_balance, account_number)
  cursor.execute(query, values)
  connection.commit()
  print("Withdrawal successful. New balance: ${:.2f}".format(new_balance))


# function to transfer money between accounts
def transfer(account_number, receiver_account_number, amount):
  current_balance = get_balance(account_number)
  if current_balance is None:
    print("Sender account does not exist")
    return
  receiver_balance = get_balance(receiver_account_number)
  if receiver_balance is None:
    print("Receiver account does not exist")
    return
  if current_balance < amount:
    print("Insufficient balance")
    return
  sender_new_balance = current_balance - amount
  receiver_new_balance = receiver_balance + amount
  query = """
        UPDATE accounts SET balance = %s WHERE account_number = %s
    """
  values = [(sender_new_balance, account_number),
            (receiver_new_balance, receiver_account_number)]
  cursor.executemany(query, values)
  connection.commit()
  print("Transfer successful. Sender's new balance: ${:.2f}".format(
    sender_new_balance))


class Bank:

  def __init__(self):
    self.accounts = {}
    self.users = {}

  def add_admin_user(self, username, password):
    self.users[username] = {'password': password, 'is_admin': True}

  def add_customer(self, first_name, last_name, username, password,
                   initial_balance):
    self.users[username] = {'password': password, 'is_admin': False}
    account_number = len(self.accounts) + 1
    self.accounts[account_number] = {
      'owner': (first_name, last_name),
      'balance': initial_balance
    }
    return account_number


bank = Bank()

# adds admin user
bank.add_admin_user("admin", "1234")
account_number = bank.add_customer("John", "Doe", "1111", "1234", 1000.00)

# main menu
while True:
  print("""
        ╭━━━━━━━━━━━━━━━━━━━━━━━╮
        ┃      Main Menu        ┃
        ├───────────────────────┤
        │ 1. Login              │
        │ 2. Create account     │
        │ 3. Exit               │
        ╰━━━━━━━━━━━━━━━━━━━━━━━╯
    """)

  choice = input("Enter your choice: ")

  if choice == "1":
    account_number = int(input("Enter account number: "))
    pin = int(input("Enter PIN: "))
    if login(account_number, pin):
      print("Login successful")
      while True:
        print("""
                    ┌───────────────────────────────┐
                    │           Your Options        │
                    ├───────────────────────────────┤
                    │ 1. Check balance   (  💰   )  │
                    │ 2. Deposit         (  💳   )  │
                    │ 3. Withdraw        (  💸   )  │
                    │ 4. Transfer        (  🔄   )  │
                    │ 5. Logout          (  🚪   )  │
                    └───────────────────────────────┘
                    """)

        option = input("Enter your choice: ")

        if option == "1":
          balance = get_balance(account_number)
          print(f"Your balance is {balance}")

        elif option == "2":
          amount = float(input("Enter amount to deposit: "))
          deposit(account_number, amount)
          print("Deposit successful")

        elif option == "3":
          amount = float(input("Enter amount to withdraw: "))
          if withdraw(account_number, amount):
            print("Withdrawal successful")

        elif option == "4":
          receiver_account_number = int(
            input("Enter receiver's account number: "))
          amount = float(input("Enter amount to transfer: "))
          if transfer(account_number, receiver_account_number, amount):
            print("Transfer successful")

        elif option == "5":
          break

        else:
          print("Invalid choice")

    else:
      print("Invalid account number or PIN")

  elif choice == "2":
    new_account()

  elif choice == "3":
    break

  else:
    print("Invalid choice")

connection.close()
