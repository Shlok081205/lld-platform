"""
Hidden test harness for the Vending Machine problem.
Expects learner's code to define classes such as:
  VendingMachine, Item / Product, Inventory,
  State (Idle, HasMoney, Dispensing, etc. — enum or state objects).

run_tests() returns a list of (name: str, passed: bool, reason: str).
"""


def run_tests():
    results = []

    def record(name, passed, reason=''):
        results.append((name, passed, reason))

    # ------------------------------------------------------------------ #
    # Utility: create a fresh machine with one item loaded
    # ------------------------------------------------------------------ #
    def _fresh_machine(item_code='A1', item_name='Cola', price=25, qty=5):
        machine = VendingMachine()
        item = Item(code=item_code, name=item_name, price=price)
        machine.add_item(item, quantity=qty)
        return machine, item

    # ------------------------------------------------------------------ #
    # 1. Add item to inventory
    # ------------------------------------------------------------------ #
    try:
        machine, item = _fresh_machine()
        qty = machine.get_quantity('A1') if hasattr(machine, 'get_quantity') else machine.inventory.get('A1', 0)
        if hasattr(qty, 'quantity'):
            qty = qty.quantity
        assert int(qty) == 5, f'Expected quantity 5, got {qty}'
        record('add_item_to_inventory', True)
    except AssertionError as e:
        record('add_item_to_inventory', False, str(e))
    except (AttributeError, TypeError, NameError) as e:
        record('add_item_to_inventory', False, f'{type(e).__name__}: {e}')

    # ------------------------------------------------------------------ #
    # 2. Select item + insert exact money — dispense item
    # ------------------------------------------------------------------ #
    try:
        machine, item = _fresh_machine(price=30)
        machine.select_item('A1')
        machine.insert_coin(30)
        dispensed = machine.dispense()
        assert dispensed is not None, 'dispense() returned None — expected an Item'
        name = dispensed.name if hasattr(dispensed, 'name') else str(dispensed)
        assert 'Cola' in name or dispensed == item or dispensed is not None, \
            f'Unexpected dispensed item: {dispensed}'
        record('dispense_exact_money', True)
    except AssertionError as e:
        record('dispense_exact_money', False, str(e))
    except (AttributeError, TypeError, NameError) as e:
        record('dispense_exact_money', False, f'{type(e).__name__}: {e}')

    # ------------------------------------------------------------------ #
    # 3. Insert more money than price — get change
    # ------------------------------------------------------------------ #
    try:
        machine, item = _fresh_machine(price=20)
        machine.select_item('A1')
        machine.insert_coin(50)
        machine.dispense()
        change = machine.return_change() if hasattr(machine, 'return_change') else machine.get_change()
        assert change is not None, 'return_change() returned None'
        assert float(change) == 30.0, f'Expected change 30, got {change}'
        record('get_change_overpayment', True)
    except AssertionError as e:
        record('get_change_overpayment', False, str(e))
    except (AttributeError, TypeError, NameError) as e:
        record('get_change_overpayment', False, f'{type(e).__name__}: {e}')

    # ------------------------------------------------------------------ #
    # 4. Select out-of-stock item — error
    # ------------------------------------------------------------------ #
    try:
        machine = VendingMachine()
        item = Item(code='B1', name='Chips', price=15)
        machine.add_item(item, quantity=0)   # 0 stock
        result = None
        try:
            result = machine.select_item('B1')
        except Exception:
            result = None
        assert result is None or result is False, \
            'Selecting out-of-stock item should fail (None/False/exception)'
        record('out_of_stock_error', True)
    except AssertionError as e:
        record('out_of_stock_error', False, str(e))
    except (AttributeError, TypeError, NameError) as e:
        record('out_of_stock_error', False, f'{type(e).__name__}: {e}')

    # ------------------------------------------------------------------ #
    # 5. Insert insufficient money — dispense should fail
    # ------------------------------------------------------------------ #
    try:
        machine, item = _fresh_machine(price=40)
        machine.select_item('A1')
        machine.insert_coin(10)   # Only 10, need 40
        result = None
        try:
            result = machine.dispense()
        except Exception:
            result = None
        assert result is None or result is False, \
            'dispense() should fail when inserted money < price'
        record('insufficient_money_error', True)
    except AssertionError as e:
        record('insufficient_money_error', False, str(e))
    except (AttributeError, TypeError, NameError) as e:
        record('insufficient_money_error', False, f'{type(e).__name__}: {e}')

    # ------------------------------------------------------------------ #
    # 6. Cancel transaction — get money back
    # ------------------------------------------------------------------ #
    try:
        machine, item = _fresh_machine(price=50)
        machine.select_item('A1')
        machine.insert_coin(30)
        refund = machine.cancel()
        assert refund is not None, 'cancel() returned None — expected refund amount'
        assert float(refund) == 30.0, f'Expected refund 30, got {refund}'
        record('cancel_refunds_money', True)
    except AssertionError as e:
        record('cancel_refunds_money', False, str(e))
    except (AttributeError, TypeError, NameError) as e:
        record('cancel_refunds_money', False, f'{type(e).__name__}: {e}')

    # ------------------------------------------------------------------ #
    # 7. Item quantity decreases after purchase
    # ------------------------------------------------------------------ #
    try:
        machine, item = _fresh_machine(price=10, qty=3)
        machine.select_item('A1')
        machine.insert_coin(10)
        machine.dispense()
        qty_after = machine.get_quantity('A1') if hasattr(machine, 'get_quantity') else machine.inventory.get('A1', 0)
        if hasattr(qty_after, 'quantity'):
            qty_after = qty_after.quantity
        assert int(qty_after) == 2, f'Expected quantity 2 after purchase, got {qty_after}'
        record('quantity_decreases_after_purchase', True)
    except AssertionError as e:
        record('quantity_decreases_after_purchase', False, str(e))
    except (AttributeError, TypeError, NameError) as e:
        record('quantity_decreases_after_purchase', False, f'{type(e).__name__}: {e}')

    # ------------------------------------------------------------------ #
    # 8. Machine in IDLE state initially
    # ------------------------------------------------------------------ #
    try:
        machine = VendingMachine()
        state = machine.state if hasattr(machine, 'state') else machine.current_state
        # Accept enum value, string, or state object
        state_str = str(state).upper() if state else ''
        assert (
            'IDLE' in state_str
            or state == 'IDLE'
            or (hasattr(state, 'name') and 'IDLE' in str(state.name).upper())
            or (hasattr(state, '__class__') and 'IDLE' in state.__class__.__name__.upper())
        ), f'Expected IDLE state initially, got: {state}'
        record('initial_idle_state', True)
    except AssertionError as e:
        record('initial_idle_state', False, str(e))
    except (AttributeError, TypeError, NameError) as e:
        record('initial_idle_state', False, f'{type(e).__name__}: {e}')

    return results
