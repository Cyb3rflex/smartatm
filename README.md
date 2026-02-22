# SmartATM - Production-Quality ATM System

A sophisticated banking system prototype built with Python, featuring clean architecture, separation of concerns, and both CLI and GUI interfaces using a shared business logic layer.

## Features

### Core Banking Operations

- ✅ **Account Management**: Create accounts with 4-digit PIN, prevent duplicates
- ✅ **Authentication**: Secure login with configurable max attempt limits
- ✅ **Balance Inquiry**: Check account balance at any time
- ✅ **Deposits**: Add funds to account with validation
- ✅ **Withdrawals**: Withdraw funds with insufficient balance checks
- ✅ **Transaction History**: Full audit trail with timestamps

### Security & Validation

- ✅ Input validation on all operations
- ✅ Configurable maximum login attempts (default: 3)
- ✅ PIN storage designed for easy transition to hashing (bcrypt, argon2, etc.)
- ✅ Transaction amount limits and validation
- ✅ Thread-safe database operations

### Architecture

- ✅ **Clean Architecture**: Clear separation of concerns
- ✅ **Service Layer**: All business logic isolated from UI
- ✅ **Repository Pattern**: Abstracted data access layer
- ✅ **Dataclasses**: Type-safe models with automatic serialization
- ✅ **No Code Duplication**: CLI and GUI share identical business logic

### Interfaces

- ✅ **CLI**: Menu-driven command-line interface
- ✅ **GUI**: Full Tkinter graphical interface with multiple screens
- ✅ **Mode Selection**: Choose interface at startup or via command-line arguments

### Data Persistence

- ✅ **JSON Storage**: Human-readable file format for easy inspection
- ✅ **Thread-Safe Operations**: Lock-based concurrency control
- ✅ **Automatic Serialization**: Models convert to/from JSON seamlessly

## Project Structure

```
smartatm/
├── atm_system/
│   ├── __init__.py           # Package initialization and exports
│   ├── config.py             # Configuration constants and settings
│   ├── models.py             # Data models (Account, Transaction)
│   ├── database.py           # JSON persistence layer
│   ├── services.py           # Business logic (core domain)
│   ├── cli.py                # Command-line interface
│   ├── gui.py                # Tkinter graphical interface
│   └── main.py               # Application entry point
├── data/
│   └── accounts.json         # Persistent account storage
├── requirements.txt          # Python dependencies
├── README.md                 # This file
└── .gitignore               # Git ignore rules
```

## Installation & Setup

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

### Step 1: Clone or Navigate to Project

```bash
cd /home/cyberflex/repos/smartatm
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
# No external dependencies required!
# The project uses only Python standard library:
# - tkinter (included with Python)
# - json (standard library)
# - dataclasses (standard library, Python 3.7+)
# - threading (standard library)
```

If you want to create a requirements.txt for documentation:

```bash
pip freeze > requirements.txt
```

## Quick Start

### Running the Application

#### Interactive Mode (Choose Interface)

```bash
python -m atm_system
```

This will present a menu to choose between CLI or GUI.

#### Run CLI Directly

```bash
python -m atm_system --cli
```

#### Run GUI Directly

```bash
python -m atm_system --gui
```

### Test Users (After Creation)

The system stores accounts in `data/accounts.json`. Create your first account:

**CLI Example:**

```
1. Login to existing account
2. Create new account
> 2
Enter desired username (min 3 characters): john
Enter 4-digit PIN: 1234
Confirm PIN: 1234
✓ Account 'john' created successfully
```

## Architecture & Design

### Design Patterns Used

1. **Repository Pattern** (database.py)
   - Abstracts data access
   - Database operations isolated from business logic
   - Easy to swap implementation (JSON → SQL, etc.)

2. **Service Layer Pattern** (services.py)
   - All business logic in one place
   - No UI dependencies
   - Reusable across interfaces
   - Easy to test

3. **MVC Pattern** (cli.py, gui.py)
   - Clean separation of View from Model/Controller
   - Methods for display logic (`print_*`, `show_*`)
   - Delegation to service layer for all operations

4. **Data Transfer Objects** (models.py)
   - Dataclasses for type safety
   - Automatic serialization with `to_dict()`/`from_dict()`
   - Clear intent and validation

### Key Design Decisions

#### 1. Both Interfaces Share Services

```python
# Same service used by both CLI and GUI
db = ATMDatabase()
service = ATMService(db)

# CLI uses it
cli = ATMCLI(service)

# GUI uses it
gui = ATMGUI(root, service)
```

**Benefit**: No duplicated business logic. Changes to rules apply everywhere.

#### 2. PIN Storage Design

Currently, PINs are stored in plaintext:

```python
# In models.py Account.pin: str
```

**For Production**, implement hashing by modifying just the services layer:

```python
# services.py authenticate() method
if not verify_password_hash(pin, account.pin_hash):
    return False
```

The dataclass structure supports this without changes to database/UI code.

#### 3. Transaction History

Each account maintains a list of transactions:

```python
@dataclass
class Transaction:
    timestamp: str          # ISO format for portability
    transaction_type: str   # 'DEPOSIT' or 'WITHDRAWAL'
    amount: float          # Decimal saved as float
    balance_after: float   # Audit trail
```

**Benefit**: Full traceability, supports regulatory requirements.

#### 4. Thread-Safe Database

The database uses `threading.RLock()`:

```python
class ATMDatabase:
    def __init__(self):
        self._lock = threading.RLock()
```

**Benefit**: Safe concurrent access if operations overlap.

#### 5. Configuration Centralization

All constants in `config.py`:

```python
MAX_LOGIN_ATTEMPTS = 3
MIN_PIN_LENGTH = 4
MAX_WITHDRAWAL_AMOUNT = 10000.00
```

**Benefit**: Change settings without touching business logic.

## API Reference

### ATMService

#### Authentication

```python
# Create account
success, message = service.create_account("john", "1234")

# Authenticate
success, message = service.authenticate("john", "1234")

# Check if authenticated
if service.is_authenticated():
    username = service.get_current_username()

# Logout
service.logout()
```

#### Operations

```python
# Check balance
success, balance, message = service.get_balance()

# Deposit
success, message = service.deposit(100.50)

# Withdraw
success, message = service.withdraw(50.00)

# Get transaction history
success, transactions, message = service.get_transaction_history(limit=10)

# Formatted history for display
history_text = service.get_formatted_transaction_history(limit=10)
```

### ATMDatabase

```python
db = ATMDatabase()

# Create account
account = Account(username="john", pin="1234")
success = db.create_account(account)

# Retrieve account
account = db.get_account("john")

# Update account
success = db.update_account(account)

# Check existence
exists = db.account_exists("john")

# Get all accounts
all_accounts = db.get_all_accounts()

# Delete account
success = db.delete_account("john")
```

## Usage Examples

### CLI Example Session

```
============================================================
                   Welcome to SmartATM
============================================================

Authentication Menu
------------------------------------------------------------
1. Login to existing account
2. Create new account
3. Exit

Enter your choice (1-3): 2

Create New Account
------------------------------------------------------------
Enter desired username (min 3 characters): alice
Enter 4-digit PIN (min 3 characters): 5678
Confirm PIN: 5678
✓ Account 'alice' created successfully

Authentication Menu
------------------------------------------------------------
1. Login to existing account
2. Create new account
3. Exit

Enter your choice (1-3): 1

Login
------------------------------------------------------------
Enter username: alice
Enter PIN: 5678
✓ Welcome, alice!

ATM Menu - alice
------------------------------------------------------------
1. Check Balance
2. Deposit Funds
3. Withdraw Funds
4. Transaction History
5. Logout

Enter your choice (1-5): 2

Deposit Funds
------------------------------------------------------------
Enter deposit amount: $1000
✓ Deposited $1000.00. New balance: $1000.00

ATM Menu - alice
------------------------------------------------------------
1. Check Balance
2. Deposit Funds
3. Withdraw Funds
4. Transaction History
5. Logout

Enter your choice (1-5): 4

Transaction History (Last 10 transactions):
======================================================================
Date/Time                 Type         Amount         Balance
----------------------------------------------------------------------
2026-02-21 14:25:30       DEPOSIT            1000.00       1000.00
======================================================================
```

### GUI Features

1. **Login Screen**
   - Username and PIN fields
   - Register and Exit options
   - Input validation

2. **Dashboard**
   - Large balance display
   - Quick action buttons
   - Username greeting

3. **Deposit/Withdraw**
   - Amount input field
   - Confirm/Cancel buttons
   - Success/error feedback

4. **Transaction History**
   - Scrollable list with formatting
   - Timestamp, type, amount, balance
   - Professional appearance

## File Format

### accounts.json

```json
{
  "alice": {
    "username": "alice",
    "pin": "5678",
    "balance": 1000.0,
    "created_at": "2026-02-21T14:25:30.123456",
    "transactions": [
      {
        "timestamp": "2026-02-21T14:25:30.123456",
        "transaction_type": "DEPOSIT",
        "amount": 1000.0,
        "balance_after": 1000.0
      }
    ]
  },
  "bob": {
    "username": "bob",
    "pin": "9999",
    "balance": 250.5,
    "created_at": "2026-02-21T14:20:00.000000",
    "transactions": [
      {
        "timestamp": "2026-02-21T14:20:15.000000",
        "transaction_type": "DEPOSIT",
        "amount": 250.5,
        "balance_after": 250.5
      }
    ]
  }
}
```

## Testing

### Manual Testing Checklist

- [ ] Create account with valid credentials
- [ ] Attempt to create duplicate account (should fail)
- [ ] Login with correct credentials
- [ ] Attempt login with incorrect PIN (verify attempt counter)
- [ ] Check balance when balance is 0
- [ ] Deposit valid amount
- [ ] Attempt deposit with negative amount
- [ ] Attempt withdraw with insufficient funds
- [ ] Successful withdrawal
- [ ] View transaction history
- [ ] Logout and re-login
- [ ] Try both CLI and GUI

### Example Test Script

```python
from atm_system import ATMService, ATMDatabase
import os

# Create test database
db = ATMDatabase()

# Clear test data
if os.path.exists('data/accounts.json'):
    import json
    with open('data/accounts.json', 'w') as f:
        json.dump({}, f)

service = ATMService(db)

# Test 1: Create account
success, msg = service.create_account("testuser", "1111")
assert success, f"Create account failed: {msg}"
print("✓ Create account works")

# Test 2: Authenticate
success, msg = service.authenticate("testuser", "1111")
assert success, f"Auth failed: {msg}"
print("✓ Authentication works")

# Test 3: Deposit
success, msg = service.deposit(100)
assert success, f"Deposit failed: {msg}"
print("✓ Deposit works")

# Test 4: Check balance
success, balance, msg = service.get_balance()
assert success and balance == 100, f"Balance check failed"
print("✓ Balance check works")

# Test 5: Withdraw
success, msg = service.withdraw(50)
assert success, f"Withdraw failed: {msg}"
print("✓ Withdrawal works")

# Test 6: Get history
success, txns, msg = service.get_transaction_history()
assert success and len(txns) == 2, f"History failed"
print("✓ Transaction history works")

print("\n✓ All tests passed!")
```

## Future Improvements

### Security Enhancements

1. **PIN Hashing**: Implement bcrypt or argon2 hashing

   ```python
   # Modify services.py authenticate()
   import bcrypt
   if not bcrypt.checkpw(pin.encode(), account.pin_hash):
       return False
   ```

2. **Session Management**: Add session tokens and expiries
3. **Rate Limiting**: Implement by-IP request throttling
4. **SSL/TLS**: If moving to network-based architecture
5. **Audit Logging**: More detailed logging system

### Feature Additions

1. **User Transfer**: Transfer money between accounts
2. **Recurring Transfers**: Schedule regular transactions
3. **Interest Calculation**: Add interest accrual
4. **Card System**: Virtual debit cards with PIN/CVC
5. **Multiple Accounts**: Users can have multiple accounts
6. **Spending Categories**: Categorize transactions
7. **Budget Tracking**: Alerts when nearing budget limits
8. **Bill Payments**: Schedule bill payments

### Architecture Improvements

1. **Database Migration**: Move from JSON to SQLite/PostgreSQL
   - Only database.py needs changes
   - Services layer remains identical
2. **REST API**: Add Flask/FastAPI backend
   - Reuse ATMService layer
   - CLI/GUI become clients

3. **Unit Testing**: Comprehensive pytest suite

   ```
   tests/
   ├── test_models.py
   ├── test_services.py
   ├── test_database.py
   └── test_integration.py
   ```

4. **Configuration Management**: Use environment variables

   ```python
   # In config.py
   MAX_LOGIN_ATTEMPTS = int(os.getenv('ATM_MAX_ATTEMPTS', '3'))
   ```

5. **Logging**: Implement Python logging module
   ```python
   import logging
   logger = logging.getLogger(__name__)
   logger.info(f"Withdrawal: {amount}")
   ```

### Production Deployment

1. **Docker Containerization**: Create Dockerfile for deployment
2. **Database Backup**: Automated backup system
3. **Error Monitoring**: Integration with Sentry or similar
4. **Performance Optimization**: Caching, indexing
5. **Multi-language Support**: i18n for UI

## Code Quality Metrics

This project demonstrates:

- **No Code Duplication**: Business logic appears once
- **Single Responsibility**: Each class has one clear purpose
- **High Cohesion**: Related code grouped together
- **Low Coupling**: Interfaces abstracted, implementations swappable
- **Type Hints**: Full type annotations for clarity
- **Comprehensive Docstrings**: Every class and method documented
- **Error Handling**: Try-except with meaningful messages
- **Configuration Centralization**: All settings in one place

## Troubleshooting

### GUI Window Not Appearing

**Issue**: GUI starts but window doesn't show
**Solution**: Ensure tkinter is installed

```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# macOS
# Tkinter comes with Python from python.org

# Windows
# Tkinter is included with Python installer
```

### "No module named 'atm_system'"

**Issue**: Can't run the application
**Solution**: Make sure you're in the correct directory

```bash
cd /home/cyberflex/repos/smartatm
python -m atm_system --cli
```

### Data File Permissions

**Issue**: "Permission denied" when saving accounts
**Solution**: Check permissions on data directory

```bash
chmod 755 data/
```

### PIN Entry Issues (GUI)

**Issue**: PIN not entering correctly
**Solution**: Check that Num Lock is enabled and PIN is numeric

## License

This project is created for educational and portfolio purposes.

## Author

Created as a demonstration of production-quality Python architecture and design patterns.

---

**Version**: 1.0.0  
**Last Updated**: February 2026  
**Python Version**: 3.10+
