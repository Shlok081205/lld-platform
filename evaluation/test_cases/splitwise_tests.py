"""
Hidden test harness for the Splitwise problem.
Expects learner's code to define classes such as:
  User, Group, Expense, EqualSplit, ExactSplit, PercentageSplit,
  SplitwiseService / SplitwiseApp (or similar top-level facade).

run_tests() returns a list of (name: str, passed: bool, reason: str).
"""


def run_tests():
    results = []

    # ------------------------------------------------------------------ #
    # Helper to record a result
    # ------------------------------------------------------------------ #
    def record(name, passed, reason=''):
        results.append((name, passed, reason))

    # ------------------------------------------------------------------ #
    # 1. Create group with members
    # ------------------------------------------------------------------ #
    try:
        alice = User('alice', 'Alice')
        bob   = User('bob',   'Bob')
        carol = User('carol', 'Carol')
        group = Group('g1', 'Friends')
        group.add_member(alice)
        group.add_member(bob)
        group.add_member(carol)
        members = group.get_members() if hasattr(group, 'get_members') else group.members
        assert len(members) == 3, f'Expected 3 members, got {len(members)}'
        record('create_group_with_members', True)
    except AssertionError as e:
        record('create_group_with_members', False, str(e))
    except (AttributeError, TypeError, NameError) as e:
        record('create_group_with_members', False, f'{type(e).__name__}: {e}')

    # ------------------------------------------------------------------ #
    # 2. Add equal split expense
    # ------------------------------------------------------------------ #
    try:
        u1 = User('u1', 'Alice')
        u2 = User('u2', 'Bob')
        u3 = User('u3', 'Carol')
        svc = SplitwiseService() if 'SplitwiseService' in dir() else SplitwiseApp()
        expense = svc.add_expense(
            paid_by=u1,
            amount=300,
            description='Dinner',
            split_type='EQUAL',
            participants=[u1, u2, u3],
        )
        assert expense is not None, 'add_expense returned None'
        record('add_equal_split_expense', True)
    except AssertionError as e:
        record('add_equal_split_expense', False, str(e))
    except (AttributeError, TypeError, NameError) as e:
        record('add_equal_split_expense', False, f'{type(e).__name__}: {e}')

    # ------------------------------------------------------------------ #
    # 3. Add exact split expense
    # ------------------------------------------------------------------ #
    try:
        u1 = User('u1', 'Alice')
        u2 = User('u2', 'Bob')
        u3 = User('u3', 'Carol')
        svc = SplitwiseService() if 'SplitwiseService' in dir() else SplitwiseApp()
        expense = svc.add_expense(
            paid_by=u1,
            amount=300,
            description='Groceries',
            split_type='EXACT',
            participants=[u1, u2, u3],
            split_values=[100, 100, 100],
        )
        assert expense is not None, 'add_expense returned None'
        record('add_exact_split_expense', True)
    except AssertionError as e:
        record('add_exact_split_expense', False, str(e))
    except (AttributeError, TypeError, NameError) as e:
        record('add_exact_split_expense', False, f'{type(e).__name__}: {e}')

    # ------------------------------------------------------------------ #
    # 4. Add percentage split expense
    # ------------------------------------------------------------------ #
    try:
        u1 = User('u1', 'Alice')
        u2 = User('u2', 'Bob')
        svc = SplitwiseService() if 'SplitwiseService' in dir() else SplitwiseApp()
        expense = svc.add_expense(
            paid_by=u1,
            amount=200,
            description='Cab',
            split_type='PERCENT',
            participants=[u1, u2],
            split_values=[60, 40],
        )
        assert expense is not None, 'add_expense returned None'
        record('add_percentage_split_expense', True)
    except AssertionError as e:
        record('add_percentage_split_expense', False, str(e))
    except (AttributeError, TypeError, NameError) as e:
        record('add_percentage_split_expense', False, f'{type(e).__name__}: {e}')

    # ------------------------------------------------------------------ #
    # 5. Get balances (who owes whom)
    # ------------------------------------------------------------------ #
    try:
        u1 = User('u1', 'Alice')
        u2 = User('u2', 'Bob')
        svc = SplitwiseService() if 'SplitwiseService' in dir() else SplitwiseApp()
        svc.add_expense(
            paid_by=u1,
            amount=100,
            description='Lunch',
            split_type='EQUAL',
            participants=[u1, u2],
        )
        balances = svc.get_balances(u2)
        # Bob owes Alice 50
        assert balances is not None, 'get_balances returned None'
        # Accept either a dict {user_id: amount} or a list of Balance objects
        if isinstance(balances, dict):
            owed = balances.get(u1.id if hasattr(u1, 'id') else u1.user_id, 0)
        elif isinstance(balances, list):
            owed = sum(
                b.amount if hasattr(b, 'amount') else b
                for b in balances
            )
        else:
            owed = balances
        assert abs(float(owed) - 50.0) < 0.01, f'Expected Bob to owe 50, got {owed}'
        record('get_balances', True)
    except AssertionError as e:
        record('get_balances', False, str(e))
    except (AttributeError, TypeError, NameError) as e:
        record('get_balances', False, f'{type(e).__name__}: {e}')

    # ------------------------------------------------------------------ #
    # 6. Settle a debt
    # ------------------------------------------------------------------ #
    try:
        u1 = User('u1', 'Alice')
        u2 = User('u2', 'Bob')
        svc = SplitwiseService() if 'SplitwiseService' in dir() else SplitwiseApp()
        svc.add_expense(
            paid_by=u1,
            amount=100,
            description='Lunch',
            split_type='EQUAL',
            participants=[u1, u2],
        )
        settled = svc.settle(debtor=u2, creditor=u1, amount=50)
        # Should not raise; truthy or None both acceptable
        record('settle_debt', True)
    except (AttributeError, TypeError, NameError) as e:
        record('settle_debt', False, f'{type(e).__name__}: {e}')
    except Exception as e:
        record('settle_debt', False, f'Unexpected error: {e}')

    # ------------------------------------------------------------------ #
    # 7. Balance after settlement becomes zero
    # ------------------------------------------------------------------ #
    try:
        u1 = User('u1', 'Alice')
        u2 = User('u2', 'Bob')
        svc = SplitwiseService() if 'SplitwiseService' in dir() else SplitwiseApp()
        svc.add_expense(
            paid_by=u1,
            amount=100,
            description='Lunch',
            split_type='EQUAL',
            participants=[u1, u2],
        )
        svc.settle(debtor=u2, creditor=u1, amount=50)
        balances = svc.get_balances(u2)
        if isinstance(balances, dict):
            uid = u1.id if hasattr(u1, 'id') else u1.user_id
            owed = balances.get(uid, 0)
        elif isinstance(balances, list):
            owed = sum(
                b.amount if hasattr(b, 'amount') else b
                for b in balances
            )
        else:
            owed = balances
        assert abs(float(owed)) < 0.01, f'Expected balance 0 after settlement, got {owed}'
        record('balance_zero_after_settlement', True)
    except AssertionError as e:
        record('balance_zero_after_settlement', False, str(e))
    except (AttributeError, TypeError, NameError) as e:
        record('balance_zero_after_settlement', False, f'{type(e).__name__}: {e}')

    # ------------------------------------------------------------------ #
    # 8. Edge case: expense with single person
    # ------------------------------------------------------------------ #
    try:
        u1 = User('u1', 'Alice')
        svc = SplitwiseService() if 'SplitwiseService' in dir() else SplitwiseApp()
        expense = svc.add_expense(
            paid_by=u1,
            amount=50,
            description='Solo coffee',
            split_type='EQUAL',
            participants=[u1],
        )
        assert expense is not None, 'add_expense with single participant returned None'
        balances = svc.get_balances(u1)
        # Alice owes nothing to herself
        if isinstance(balances, dict):
            total_owed = sum(abs(float(v)) for v in balances.values())
        elif isinstance(balances, list):
            total_owed = sum(abs(float(b.amount if hasattr(b, 'amount') else b)) for b in balances)
        else:
            total_owed = float(balances) if balances else 0
        assert total_owed < 0.01, f'Expected no debt for solo expense, got {total_owed}'
        record('single_person_expense', True)
    except AssertionError as e:
        record('single_person_expense', False, str(e))
    except (AttributeError, TypeError, NameError) as e:
        record('single_person_expense', False, f'{type(e).__name__}: {e}')
    except Exception as e:
        record('single_person_expense', False, f'Unexpected: {e}')

    return results
