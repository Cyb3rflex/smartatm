# SmartATM Architecture Documentation

## Overview

SmartATM is designed using **clean architecture principles** with a clear separation of concerns. All business logic is isolated in the service layer, making the system testable, maintainable, and UI-agnostic.

## Layered Architecture

```
┌─────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                │
│          (CLI Module & GUI Module)                   │
│  - ATMCLI: Menu-driven command line interface       │
│  - ATMGUI: Tkinter-based graphical interface        │
└────────────────────┬────────────────────────────────┘
                     │ Uses
                     ↓
┌─────────────────────────────────────────────────────┐
│                   SERVICE LAYER                      │
│              (ATMService Module)                     │
│  - Authentication & Account Management              │
│  - Deposit, Withdraw, Balance Operations           │
│  - Transaction History Management                   │
│  - Input Validation & Business Rules               │
└────────────────────┬────────────────────────────────┘
                     │ Uses
                     ↓
┌─────────────────────────────────────────────────────┐
│                 PERSISTENCE LAYER                    │
│           (ATMDatabase & Models)                     │
│  - JSON file I/O operations                         │
│  - Account & Transaction models                      │
│  - Data serialization/deserialization               │
└─────────────────────────────────────────────────────┘
```

## Module Responsibilities

### 1. **config.py** - Configuration & Constants

**Purpose**: Centralize all configurable settings

**Key Elements**:

- Application constants (APP_NAME, VERSION)
- File paths (PROJECT_ROOT, ACCOUNTS_FILE)
- Security settings (MAX_LOGIN_ATTEMPTS, PIN_LENGTH)
- Transaction limits (MIN_AMOUNT, MAX_WITHDRAWAL)
- UI settings (WINDOW_WIDTH, WINDOW_HEIGHT)

**Benefits**:

- Change settings without touching code
- Environment-specific configuration
- Supports future migration to environment variables

**Example**:

```python
# Easy to adjust security level
MAX_LOGIN_ATTEMPTS = 3  # Can be changed to 5

# Easy to adjust business rules
MAX_WITHDRAWAL_AMOUNT = 10000.00  # Can be changed to 5000.00
```

### 2. **models.py** - Data Models

**Purpose**: Define domain entities with type safety

**Classes**:

- `Transaction`: Records a single banking operation
  - `timestamp`: ISO format datetime for portability
  - `transaction_type`: 'DEPOSIT' or 'WITHDRAWAL'
  - `amount`: Transaction amount
  - `balance_after`: Audit trail snapshot
- `Account`: Represents a user account
  - `username`: Unique identifier
  - `pin`: Authentication credential
  - `balance`: Current account balance
  - `transactions`: List of Transaction objects
  - `created_at`: Account creation timestamp

**Benefits**:

- Type hints prevent bugs
- Dataclasses provide automatic `__init__`, `__repr__`, etc.
- `to_dict()`/`from_dict()` methods handle serialization
- Easy to add new fields (e.g., `account_type`, `status`)

### 3. **database.py** - Persistence Layer

**Purpose**: Abstract all data I/O operations

**Class**: `ATMDatabase`

**Patterns Used**:

- **Repository Pattern**: Hides persistence implementation details
- **Thread-Safety**: Uses `threading.RLock()` for concurrent access

**Methods**:

```python
db.create_account(account)        # Create new account
db.get_account(username)          # Retrieve by username
db.update_account(account)        # Persist changes
db.account_exists(username)       # Check existence
db.delete_account(username)       # Remove account
db.get_all_accounts()             # Get all accounts
```

**Design Advantages**:

- **Easy Migration**: To switch from JSON to SQL:
  1. Keep the same interface
  2. Change only the `_read_from_file()` and `_write_to_file()` methods
  3. All service and UI code remains unchanged!

**Example Migration Path**:

```python
# Current: JSON-based
class ATMDatabase:
    def _read_from_file(self):
        with open(self.file_path) as f:
            return json.loads(f.read())

# Future: SQL-based (same public interface)
class ATMDatabaseSQL:
    def _read_from_file(self):
        return db.query(Account).all()
        # External code doesn't know or care about the change!
```

### 4. **services.py** - Business Logic Layer

**Purpose**: Contain all domain logic, independent of UI

**Class**: `ATMService`

**Key Responsibilities**:

1. **Authentication**
   - Create accounts with validation
   - Authenticate users with PIN verification
   - Track login attempts
   - Session management

2. **Banking Operations**
   - Deposit with amount validation
   - Withdraw with balance checking
   - Balance inquiry
   - Transaction recording

3. **Validation**
   - Input format validation
   - Business rule enforcement
   - Error message generation

**Design Pattern**: Service Layer

```python
class ATMService:
    def __init__(self, database: ATMDatabase):
        self.db = database          # Dependency injection
        self.current_user = None    # Session state

    def authenticate(self, username, pin) -> Tuple[bool, str]:
        # All business rules here, not in UI
        # Reusable by CLI and GUI
```

**Why This Matters**:

```python
# Without Service Layer (BAD - logic duplicated)
# cli.py
def handle_deposit(amount):
    if amount <= 0:  # Validation
        print("Invalid")
    elif amount > limit:  # More validation
        print("Too much")
    else:
        account.balance += amount  # Logic
        save_to_file(account)

# gui.py (duplicate logic!)
def handle_deposit(amount):
    if amount <= 0:  # Same checks again
        messagebox.show("Invalid")
    elif amount > limit:  # Same logic
        messagebox.show("Too much")
    ...

# With Service Layer (GOOD - single source of truth)
# services.py
def deposit(self, amount):
    if amount <= 0:
        return False, "Invalid"
    if amount > limit:
        return False, "Too much"
    # ... all logic here

# cli.py (can't duplicate - uses service)
success, msg = service.deposit(amount)
if success:
    print_success(msg)
else:
    print_error(msg)

# gui.py (same service!)
success, msg = service.deposit(amount)
if success:
    messagebox.showinfo("Success", msg)
else:
    messagebox.showerror("Error", msg)
```

### 5. **cli.py** - Command-Line Interface

**Purpose**: Terminal-based user interaction

**Class**: `ATMCLI`

**Responsibilities**:

- Display menus and prompts
- Collect user input
- Format output for terminal
- Delegate all operations to ATMService

**Structure**:

```python
class ATMCLI:
    def run(self):                  # Main loop
        while True:
            if authenticated:
                self.show_atm_menu()
            else:
                self.show_authentication_menu()

    # Menu methods
    def show_authentication_menu(self):  # Display options
    def handle_login(self):             # Handle login action
    def handle_deposit(self):           # Handle deposit action

    # Helper methods
    def print_success(self, msg):       # Formatted output
    def print_error(self, msg):
    def get_input(self, prompt):        # Safe input handling
```

**Key Design**:

- No business logic - all delegated to service
- No database access - all through service
- Focuses purely on I/O and presentation
- Easy to test (can mock the service)

### 6. **gui.py** - Graphical User Interface

**Purpose**: Tkinter-based graphical interaction

**Class**: `ATMGUI`

**Screens**:

- Login Screen (username, PIN input)
- Registration Screen (create new account)
- Dashboard (balance display, menu buttons)
- Deposit/Withdraw Screens (amount input)
- Transaction History (scrollable list)

**Design Pattern**: Same as CLI but for GUI

```python
class ATMGUI:
    def show_dashboard(self):
        # Create UI elements (frames, buttons, labels)

        # Handle button clicks
        deposit_btn.command = lambda: self.handle_deposit()

    def handle_deposit(self, amount):
        # Get amount from UI
        # Delegate to service (same as CLI!)
        success, msg = self.service.deposit(amount)

        # Show result in UI
        if success:
            messagebox.showinfo("Success", msg)
```

**Benefits of Identical Service Usage**:

```
CLI User                    GUI User
    ↓                           ↓
  ATMCLI                      ATMGUI
    ↓                           ↓
    └──────→ ATMService ←──────┘
                ↓
            ATMDatabase
                ↓
           accounts.json
```

Both interfaces see the exact same behavior!

### 7. **main.py** - Application Entry Point

**Purpose**: Bootstrap the application

**Functionality**:

- Parse command-line arguments
- Display mode selection menu
- Initialize appropriate interface

**CLI Arguments**:

```bash
python -m atm_system              # Interactive selection
python -m atm_system --cli        # Force CLI mode
python -m atm_system --gui        # Force GUI mode
python -m atm_system --version    # Show version
```

## Data Flow Examples

### Example 1: Deposit Operation

```
┌─ User presses "Deposit" button (GUI) or selects "2" (CLI)
│
└─→ GUI/CLI.handle_deposit()
    └─→ service.deposit(amount)
        ├─ Validate amount (business rule)
        ├─ Check balance (not needed for deposit)
        ├─ Update account.balance
        ├─ Create Transaction record
        └─→ db.update_account(account)
            └─ Write updated account to JSON
    ←─ Return (success: bool, message: str)
├─ GUI: messagebox.showinfo(title, message)
└─ CLI: print_success(message)
```

### Example 2: Account Creation

```
┌─ User enters username "alice" and PIN "5678"
│
└─→ GUI/CLI.handle_create_account(username, pin)
    └─→ service.create_account(username, pin)
        ├─ Validate username (length, characters)
        ├─ Validate PIN (numeric, length)
        ├─ Check for duplicates
        ├─ Create Account object
        └─→ db.create_account(account)
            └─ Check if username exists in JSON
            └─ Add new account to JSON
    ←─ Return (success: bool, message: str)
├─ GUI: Show registration result dialog
└─ CLI: Show registration result message
```

## Error Handling Strategy

**Three-Level Error Handling**:

```python
# Level 1: Input Validation (database.py)
try:
    with open(file_path) as f:
        return json.loads(f.read())
except JSONDecodeError:
    return {}  # Graceful fallback

# Level 2: Business Logic Validation (services.py)
if amount <= 0:
    return False, "Amount must be positive"

# Level 3: UI Error Display (cli.py / gui.py)
success, message = service.deposit(amount)
if success:
    print_success(message)
else:
    print_error(message)  # Never crashes, always shows user feedback
```

**Benefits**:

- No uncaught exceptions
- User always gets meaningful feedback
- Graceful degradation
- Easy to add logging/monitoring

## Security Considerations

### PIN Storage (Current)

```python
account.pin = "1234"  # Plaintext in JSON
```

### PIN Storage (Recommended for Production)

```python
# Import at top of services.py
import bcrypt

# In create_account():
pin_hash = bcrypt.hashpw(pin.encode(), bcrypt.gensalt())
account.pin_hash = pin_hash.hex()

# In authenticate():
if not bcrypt.checkpw(pin.encode(), bytes.fromhex(account.pin_hash)):
    return False, "Invalid PIN"
```

**Schema Change Needed**:

```python
# In models.py, Account dataclass:
# PIN: str  ← Remove
# PIN_HASH: str  ← Add (hash stored as hex string)
```

**Advantage of This Design**:

- Only 3 lines need to change
- No other layer is affected
- Services layer logic remains identical
- CLI and GUI work without modification

## Testing Strategy

### Unit Testing Approach

```python
# Test services without UI
def test_deposit():
    db = ATMDatabase("test_accounts.json")
    service = ATMService(db)

    service.create_account("alice", "1234")
    service.authenticate("alice", "1234")

    success, msg = service.deposit(100)
    assert success
    assert service.get_balance()[1] == 100

# Mock the service to test UI
def test_cli_deposit():
    mock_service = Mock()
    mock_service.deposit.return_value = (True, "Success")

    cli = ATMCLI(mock_service)
    cli.handle_deposit("100")

    mock_service.deposit.assert_called_with(100)
```

## Deployment Considerations

### Current State: Single Machine

- JSON storage on local filesystem
- CLI/GUI on same machine
- Single database file

### Future: Client-Server Architecture

```
Without code changes to services.py:

User (CLI)                User (GUI)
    ↓                         ↓
HTTP Client             HTTP Client
    ↓                         ↓
    └─────→ FastAPI Server ←──┘
                ↓
            ATMService (unchanged!)
                ↓
            Database (PostgreSQL)
```

The service layer would remain exactly the same!

## Performance Characteristics

### Current Bottlenecks

1. **JSON Serialization**: O(n) per operation
2. **Lock Contention**: All operations serialize through lock
3. **No Indexing**: Linear search for accounts

### Optimization Path

| Change               | Impact                       | Effort |
| -------------------- | ---------------------------- | ------ |
| Add in-memory cache  | 10x faster                   | Small  |
| Move to SQLite       | Better for concurrent access | Medium |
| Move to PostgreSQL   | Unlimited scale              | Large  |
| Add REST API + async | Multi-user support           | Large  |

**Key Point**: Services.py stays the same!

## Summary: Why This Architecture?

| Principle                       | Benefit                | Example                                     |
| ------------------------------- | ---------------------- | ------------------------------------------- |
| **Separation of Concerns**      | Each layer has one job | UI doesn't know about JSON                  |
| **DRY (Don't Repeat Yourself)** | Logic appears once     | CLI & GUI use same deposit code             |
| **Dependency Injection**        | Easy to test and mock  | Service gets database injected              |
| **Repository Pattern**          | Easy DB migration      | Swap JSON for SQL without changing services |
| **Layered Architecture**        | Easy to understand     | Flow is clear: UI → Service → Database      |

**Result**: Code that is:

- ✅ Easy to understand (layered, linear flow)
- ✅ Easy to test (each layer can be tested independently)
- ✅ Easy to maintain (changes localized to one layer)
- ✅ Easy to extend (new interfaces just use service layer)
- ✅ Production-quality (handles errors gracefully)
