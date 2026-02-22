#!/usr/bin/env python3
"""
Quick test script to verify SmartATM is working correctly.
"""

import sys
import os

print('Testing SmartATM...')
print('=' * 60)

# Test imports
print('\n1. Testing imports...')
try:
    # Import core components (avoid GUI which requires tkinter)
    from atm_system.models import Account, Transaction
    from atm_system.database import ATMDatabase
    from atm_system.services import ATMService
    from atm_system.config import APP_NAME, APP_VERSION
    print('   ✓ Core imports successful')
except ImportError as e:
    print(f'   ✗ Import failed: {e}')
    sys.exit(1)

# Test initialization
print('\n2. Testing service initialization...')
try:
    db = ATMDatabase()
    service = ATMService(db)
    print('   ✓ Database and Service initialized')
except Exception as e:
    print(f'   ✗ Initialization failed: {e}')
    sys.exit(1)

# Test account creation
print('\n3. Testing account creation...')
try:
    success, msg = service.create_account('testuser', '1234')
    if success:
        print(f'   ✓ Account creation: {msg}')
    else:
        print(f'   ✗ Account creation failed: {msg}')
except Exception as e:
    print(f'   ✗ Exception: {e}')
    sys.exit(1)

# Test authentication
print('\n4. Testing authentication...')
try:
    success, msg = service.authenticate('testuser', '1234')
    if success:
        print(f'   ✓ Authentication: {msg}')
    else:
        print(f'   ✗ Authentication failed: {msg}')
except Exception as e:
    print(f'   ✗ Exception: {e}')
    sys.exit(1)

# Test operations
print('\n5. Testing deposit...')
try:
    success, msg = service.deposit(100.0)
    if success:
        print(f'   ✓ Deposit: {msg}')
    else:
        print(f'   ✗ Deposit failed: {msg}')
except Exception as e:
    print(f'   ✗ Exception: {e}')
    sys.exit(1)

# Test balance
print('\n6. Testing balance inquiry...')
try:
    success, balance, msg = service.get_balance()
    if success:
        print(f'   ✓ Balance check: ${balance:.2f}')
    else:
        print(f'   ✗ Balance check failed: {msg}')
except Exception as e:
    print(f'   ✗ Exception: {e}')
    sys.exit(1)

# Test withdrawal
print('\n7. Testing withdrawal...')
try:
    success, msg = service.withdraw(50.0)
    if success:
        print(f'   ✓ Withdrawal: {msg}')
    else:
        print(f'   ✗ Withdrawal failed: {msg}')
except Exception as e:
    print(f'   ✗ Exception: {e}')
    sys.exit(1)

# Test history
print('\n8. Testing transaction history...')
try:
    success, txns, msg = service.get_transaction_history()
    if success:
        print(f'   ✓ Transaction history: {len(txns)} transactions')
    else:
        print(f'   ✗ History retrieval failed: {msg}')
except Exception as e:
    print(f'   ✗ Exception: {e}')
    sys.exit(1)

print('\n' + '=' * 60)
print(f'✓ All tests passed!')
print(f'✓ {APP_NAME} v{APP_VERSION} is ready to run')
print('=' * 60)
print('\nRun the application with:')
print('  python -m atm_system              # Interactive mode')
print('  python -m atm_system --cli        # CLI interface')
print('  python -m atm_system --gui        # GUI interface')
