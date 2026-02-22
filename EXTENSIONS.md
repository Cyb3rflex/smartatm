# SmartATM Extensions & Examples

This document provides code examples for extending SmartATM with new features while maintaining clean architecture.

## Extension Pattern

All extensions follow this pattern:

1. **Add to models.py** if new data types needed
2. **Add to config.py** if new settings needed
3. **Add to services.py** for business logic
4. **Update cli.py and gui.py** identically for both interfaces

## Example 1: Add PIN Change Functionality

### Step 1: Add to services.py

```python
# In ATMService class, add:

def change_pin(self, old_pin: str, new_pin: str) -> Tuple[bool, str]:
    """
    Change PIN for current user.

    Args:
        old_pin: Current PIN for verification
        new_pin: New PIN

    Returns:
        (success: bool, message: str)
    """
    if not self.is_authenticated():
        return False, "Not authenticated"

    # Verify old PIN
    if self.current_user.pin != old_pin:
        return False, "Current PIN is incorrect"

    # Validate new PIN
    if len(new_pin) != MAX_PIN_LENGTH or not new_pin.isdigit():
        return False, f"PIN must be {MAX_PIN_LENGTH} digits"

    # Update PIN
    self.current_user.pin = new_pin
    self.current_user.add_transaction('PIN_CHANGE', 0)

    # Persist
    if not self.db.update_account(self.current_user):
        return False, "Failed to update PIN (database error)"

    return True, "PIN changed successfully"
```

### Step 2: Add to cli.py

```python
# In the ATM menu, update options:
def show_atm_menu(self) -> None:
    # ... existing options ...
    print("5. Change PIN")       # ← Add this
    print("6. Transaction History")
    print("7. Logout")

# Add handler:
def handle_change_pin(self) -> None:
    """Handle PIN change."""
    self.print_section("Change PIN")

    old_pin = self.get_input("Enter current PIN: ")
    new_pin = self.get_input("Enter new PIN: ")
    new_pin_confirm = self.get_input("Confirm new PIN: ")

    if new_pin != new_pin_confirm:
        self.print_error("New PINs do not match")
        return

    success, message = self.service.change_pin(old_pin, new_pin)

    if success:
        self.print_success(message)
    else:
        self.print_error(message)

# Update menu handler:
elif choice == "5":
    self.handle_change_pin()
```

### Step 3: Add to gui.py

```python
# In dashboard button frame, add:
change_pin_btn = self.create_button(
    button_frame,
    "Change PIN",
    self.show_change_pin_screen,
    bg_color="#16a085"
)
change_pin_btn.pack(pady=5, fill=tk.X, padx=30)

# Add screen method:
def show_change_pin_screen(self) -> None:
    """Display PIN change screen."""
    self.clear_window()
    frame = self.create_frame()

    self.create_header(frame, "Change PIN")

    old_pin = self.create_label_entry(frame, "Current PIN:", is_password=True)
    new_pin = self.create_label_entry(frame, "New PIN:", is_password=True)
    new_pin_confirm = self.create_label_entry(frame, "Confirm PIN:", is_password=True)

    button_frame = tk.Frame(frame, bg="#f0f0f0")
    button_frame.pack(pady=20)

    change_btn = self.create_button(
        button_frame,
        "Change PIN",
        lambda: self.handle_change_pin(
            old_pin.get(),
            new_pin.get(),
            new_pin_confirm.get()
        ),
        bg_color="#16a085"
    )
    change_btn.pack(side=tk.LEFT, padx=10)

    back_btn = self.create_button(
        button_frame,
        "Cancel",
        self.show_dashboard,
        bg_color="#95a5a6"
    )
    back_btn.pack(side=tk.LEFT, padx=10)

def handle_change_pin(self, old_pin: str, new_pin: str, new_pin_confirm: str) -> None:
    """Handle PIN change."""
    if new_pin != new_pin_confirm:
        self.show_error("Error", "New PINs do not match")
        return

    success, message = self.service.change_pin(old_pin, new_pin)

    if success:
        self.show_success("PIN Changed", message)
        self.show_dashboard()
    else:
        self.show_error("Failed", message)
```

## Example 2: Add Account Statement Export

### Step 1: Add to services.py

```python
def export_statement(self, filename: str) -> Tuple[bool, str]:
    """
    Export transaction history to file.

    Args:
        filename: File to write statement to

    Returns:
        (success: bool, message: str)
    """
    if not self.is_authenticated():
        return False, "Not authenticated"

    try:
        with open(filename, 'w') as f:
            f.write(f"Account Statement - {self.current_user.username}\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write(f"Current Balance: ${self.current_user.balance:.2f}\n")
            f.write("=" * 70 + "\n\n")

            f.write(self.get_formatted_transaction_history())

        return True, f"Statement saved to {filename}"

    except IOError as e:
        return False, f"Failed to write file: {str(e)}"
```

### Step 2: Add to cli.py

```python
def handle_export_statement(self) -> None:
    """Handle statement export."""
    self.print_section("Export Statement")

    filename = self.get_input("Enter filename (e.g., statement.txt): ")
    if not filename:
        self.print_error("Cancelled")
        return

    success, message = self.service.export_statement(filename)

    if success:
        self.print_success(message)
    else:
        self.print_error(message)

# Add to menu
print("6. Export Statement")
```

## Example 3: Add Transfer Between Accounts

### Step 1: Update models.py

```python
# Add to Transaction to track transfer recipient:
@dataclass
class Transaction:
    # ... existing fields ...
    recipient: Optional[str] = None  # For transfers
```

### Step 2: Add to services.py

```python
def transfer(self, recipient_username: str, amount: float) -> Tuple[bool, str]:
    """
    Transfer funds to another account.

    Args:
        recipient_username: Username to transfer to
        amount: Amount to transfer

    Returns:
        (success: bool, message: str)
    """
    if not self.is_authenticated():
        return False, "Not authenticated"

    # Validate amount
    if amount <= 0:
        return False, "Transfer amount must be positive"

    if amount > self.current_user.balance:
        return False, "Insufficient funds"

    # Get recipient account
    recipient = self.db.get_account(recipient_username)
    if recipient is None:
        return False, "Recipient account not found"

    # Perform transfer
    self.current_user.balance -= amount
    self.current_user.add_transaction('TRANSFER', amount)

    recipient.balance += amount
    recipient.add_transaction('TRANSFER_RECEIVED', amount)

    # Persist both
    if not self.db.update_account(self.current_user):
        return False, "Transfer failed"

    if not self.db.update_account(recipient):
        # Rollback
        self.current_user.balance += amount
        self.db.update_account(self.current_user)
        return False, "Transfer failed"

    return True, f"Transferred ${amount:.2f} to {recipient_username}"
```

### Step 3: Add to cli.py

```python
def handle_transfer(self) -> None:
    """Handle transfer operation."""
    self.print_section("Transfer Funds")

    recipient = self.get_input("Enter recipient username: ")
    amount_str = self.get_input("Enter amount: $")

    try:
        amount = float(amount_str)
        success, message = self.service.transfer(recipient, amount)

        if success:
            self.print_success(message)
        else:
            self.print_error(message)

    except ValueError:
        self.print_error("Invalid amount")
```

## Example 4: Add Interest Accrual

### Step 1: Update models.py

```python
@dataclass
class Account:
    # ... existing fields ...
    interest_rate: float = 0.02  # 2% annual
    last_interest_date: str = field(default_factory=lambda: datetime.now().isoformat())
```

### Step 2: Add to services.py

```python
def apply_interest(self) -> Tuple[bool, str]:
    """
    Calculate and apply interest to account.

    Returns:
        (success: bool, message: str)
    """
    if not self.is_authenticated():
        return False, "Not authenticated"

    # Calculate interest
    last_date = datetime.fromisoformat(self.current_user.last_interest_date)
    days_elapsed = (datetime.now() - last_date).days

    if days_elapsed == 0:
        return False, "Interest already applied today"

    interest = self.current_user.balance * self.current_user.interest_rate * (days_elapsed / 365)

    # Apply interest
    self.current_user.balance += interest
    self.current_user.add_transaction('INTEREST', interest)
    self.current_user.last_interest_date = datetime.now().isoformat()

    # Persist
    if not self.db.update_account(self.current_user):
        return False, "Failed to apply interest"

    return True, f"Interest applied: ${interest:.2f}"
```

## Example 5: Add Transaction Categories

### Step 1: Update models.py

```python
@dataclass
class Transaction:
    # ... existing fields ...
    category: str = "General"  # 'Salary', 'Bills', 'Shopping', etc.
```

### Step 2: Add to services.py

```python
def analyze_spending(self) -> Dict[str, float]:
    """
    Analyze spending by category.

    Returns:
        Dictionary mapping category to total amount
    """
    if not self.is_authenticated():
        return {}

    category_totals = {}

    for txn in self.current_user.transactions:
        if txn.transaction_type == 'WITHDRAWAL':
            category = txn.category
            category_totals[category] = category_totals.get(category, 0) + txn.amount

    return category_totals
```

## Example 6: REST API Interface

### Using Flask

```python
# new_file: api.py

from flask import Flask, jsonify, request
from atm_system import ATMService, ATMDatabase

app = Flask(__name__)
db = ATMDatabase()
service = ATMService(db)

@app.route('/api/accounts', methods=['POST'])
def create_account():
    """Create account via API."""
    data = request.json
    success, msg = service.create_account(
        data['username'],
        data['pin']
    )
    return jsonify({'success': success, 'message': msg})

@app.route('/api/login', methods=['POST'])
def login():
    """Authenticate user."""
    data = request.json
    success, msg = service.authenticate(
        data['username'],
        data['pin']
    )
    return jsonify({'success': success, 'message': msg})

@app.route('/api/balance', methods=['GET'])
def get_balance():
    """Get balance."""
    success, balance, msg = service.get_balance()
    return jsonify({
        'success': success,
        'balance': balance,
        'message': msg
    })

@app.route('/api/deposit', methods=['POST'])
def deposit():
    """Deposit funds."""
    data = request.json
    success, msg = service.deposit(data['amount'])
    return jsonify({'success': success, 'message': msg})

# Run: python api.py
# Access: http://localhost:5000/api/balance
```

## Example 7: Add Unit Tests

```python
# new_file: tests/test_services.py

import pytest
from atm_system import ATMService, ATMDatabase, Account

@pytest.fixture
def service():
    """Create service with test database."""
    db = ATMDatabase("test_accounts.json")
    return ATMService(db)

def test_create_account(service):
    """Test account creation."""
    success, msg = service.create_account("testuser", "1234")
    assert success
    assert "created" in msg.lower()

def test_duplicate_account(service):
    """Test duplicate prevention."""
    service.create_account("testuser", "1234")
    success, msg = service.create_account("testuser", "1234")
    assert not success
    assert "already exists" in msg.lower()

def test_authenticate(service):
    """Test authentication."""
    service.create_account("testuser", "1234")
    success, msg = service.authenticate("testuser", "1234")
    assert success

def test_invalid_pin(service):
    """Test invalid PIN."""
    service.create_account("testuser", "1234")
    success, msg = service.authenticate("testuser", "0000")
    assert not success

def test_deposit(service):
    """Test deposit."""
    service.create_account("testuser", "1234")
    service.authenticate("testuser", "1234")
    success, msg = service.deposit(100)
    assert success

def test_insufficient_funds(service):
    """Test withdrawal with insufficient funds."""
    service.create_account("testuser", "1234")
    service.authenticate("testuser", "1234")
    service.deposit(50)
    success, msg = service.withdraw(100)
    assert not success
    assert "insufficient" in msg.lower()

# Run: pytest test_services.py
```

## Design Principles for Extensions

### 1. **Keep Services Independent**

Extensions should not require changes to other services. Each feature is self-contained.

### 2. **Follow the Separation Pattern**

- Models → Data structures
- Services → Business logic
- UI → Display logic

### 3. **Handle Errors Gracefully**

```python
# Good
return False, "Specific error message"

# Bad
raise Exception("error")
```

### 4. **Type Hints for Clarity**

```python
# Good
def transfer(self, recipient: str, amount: float) -> Tuple[bool, str]:

# Bad
def transfer(self, recipient, amount):
```

### 5. **Test Before Integrating**

Write tests for new features in services.py before adding to UI.

## Testing Checklist for New Features

- [ ] Service layer works in isolation
- [ ] Handles invalid input gracefully
- [ ] Valid input succeeds
- [ ] Error messages are meaningful
- [ ] State persists correctly
- [ ] CLI implementation works
- [ ] GUI implementation works
- [ ] Both interfaces show same error messages

## Performance Notes

For extensions, consider:

1. **Large Datasets**: Use pagination for transaction history
2. **Concurrent Access**: Database uses locks (adequate for small scale)
3. **Memory Usage**: Don't load all accounts for single user
4. **Response Time**: Keep service methods under 100ms

## Conclusion

SmartATM's architecture makes it easy to add features without breaking existing code. The separation of concerns ensures:

- **New features are isolated** (don't affect existing code)
- **Both interfaces get updates automatically** (use same service)
- **Testing is straightforward** (can test services independently)
- **Maintenance is simple** (changes localized to one layer)
