"""
Hidden test harness for the Library Management problem.
Expects learner's code to define classes such as:
  Book, Member, Library, LibraryService / LibrarySystem,
  Reservation, Fine (or similar).

run_tests() returns a list of (name: str, passed: bool, reason: str).
"""
from datetime import datetime, timedelta


def run_tests():
    results = []

    def record(name, passed, reason=''):
        results.append((name, passed, reason))

    # ------------------------------------------------------------------ #
    # 1. Add book to library
    # ------------------------------------------------------------------ #
    try:
        lib = Library('City Library') if 'Library' in dir() else LibraryService()
        book = Book(isbn='978-0-13-110362-7', title='The C Programming Language', author='Kernighan')
        lib.add_book(book)
        found = lib.search_by_isbn('978-0-13-110362-7') if hasattr(lib, 'search_by_isbn') else lib.get_book('978-0-13-110362-7')
        assert found is not None, 'Added book not found via search'
        record('add_book', True)
    except AssertionError as e:
        record('add_book', False, str(e))
    except (AttributeError, TypeError, NameError) as e:
        record('add_book', False, f'{type(e).__name__}: {e}')

    # ------------------------------------------------------------------ #
    # 2. Member can borrow a book
    # ------------------------------------------------------------------ #
    try:
        lib = Library('City Library') if 'Library' in dir() else LibraryService()
        book = Book(isbn='ISBN-001', title='Clean Code', author='Martin')
        lib.add_book(book)
        member = Member(member_id='M001', name='Alice')
        lib.add_member(member)
        loan = lib.borrow(member_id='M001', isbn='ISBN-001')
        assert loan is not None, 'borrow() returned None — expected a Loan/Record'
        record('member_borrow_book', True)
    except AssertionError as e:
        record('member_borrow_book', False, str(e))
    except (AttributeError, TypeError, NameError) as e:
        record('member_borrow_book', False, f'{type(e).__name__}: {e}')

    # ------------------------------------------------------------------ #
    # 3. Borrowed book is unavailable to others
    # ------------------------------------------------------------------ #
    try:
        lib = Library('City Library') if 'Library' in dir() else LibraryService()
        book = Book(isbn='ISBN-002', title='DDIA', author='Kleppmann')
        lib.add_book(book)
        m1 = Member(member_id='M001', name='Alice')
        m2 = Member(member_id='M002', name='Bob')
        lib.add_member(m1)
        lib.add_member(m2)
        lib.borrow(member_id='M001', isbn='ISBN-002')
        # Second borrow attempt should fail (return None, False, or raise)
        result = None
        try:
            result = lib.borrow(member_id='M002', isbn='ISBN-002')
        except Exception:
            result = None
        assert result is None or result is False, \
            'Borrowed book should not be borrowable by another member'
        record('borrowed_book_unavailable', True)
    except AssertionError as e:
        record('borrowed_book_unavailable', False, str(e))
    except (AttributeError, TypeError, NameError) as e:
        record('borrowed_book_unavailable', False, f'{type(e).__name__}: {e}')

    # ------------------------------------------------------------------ #
    # 4. Member returns book — book becomes available
    # ------------------------------------------------------------------ #
    try:
        lib = Library('City Library') if 'Library' in dir() else LibraryService()
        book = Book(isbn='ISBN-003', title='Refactoring', author='Fowler')
        lib.add_book(book)
        m1 = Member(member_id='M001', name='Alice')
        m2 = Member(member_id='M002', name='Bob')
        lib.add_member(m1)
        lib.add_member(m2)
        lib.borrow(member_id='M001', isbn='ISBN-003')
        lib.return_book(member_id='M001', isbn='ISBN-003')
        loan2 = lib.borrow(member_id='M002', isbn='ISBN-003')
        assert loan2 is not None, 'After return, book should be available for next member'
        record('return_book_becomes_available', True)
    except AssertionError as e:
        record('return_book_becomes_available', False, str(e))
    except (AttributeError, TypeError, NameError) as e:
        record('return_book_becomes_available', False, f'{type(e).__name__}: {e}')

    # ------------------------------------------------------------------ #
    # 5. Reserve a book that is currently borrowed
    # ------------------------------------------------------------------ #
    try:
        lib = Library('City Library') if 'Library' in dir() else LibraryService()
        book = Book(isbn='ISBN-004', title='GoF Patterns', author='Gang of Four')
        lib.add_book(book)
        m1 = Member(member_id='M001', name='Alice')
        m2 = Member(member_id='M002', name='Bob')
        lib.add_member(m1)
        lib.add_member(m2)
        lib.borrow(member_id='M001', isbn='ISBN-004')
        reservation = lib.reserve(member_id='M002', isbn='ISBN-004')
        assert reservation is not None, 'reserve() returned None — expected a Reservation object'
        record('reserve_borrowed_book', True)
    except AssertionError as e:
        record('reserve_borrowed_book', False, str(e))
    except (AttributeError, TypeError, NameError) as e:
        record('reserve_borrowed_book', False, f'{type(e).__name__}: {e}')

    # ------------------------------------------------------------------ #
    # 6. Fine calculation for overdue return
    # ------------------------------------------------------------------ #
    try:
        lib = Library('City Library') if 'Library' in dir() else LibraryService()
        book = Book(isbn='ISBN-005', title='Pragmatic Programmer', author='Hunt')
        lib.add_book(book)
        member = Member(member_id='M001', name='Alice')
        lib.add_member(member)
        loan = lib.borrow(member_id='M001', isbn='ISBN-005')

        # Force the due_date to be 5 days in the past
        overdue_date = datetime.now() - timedelta(days=5)
        if hasattr(loan, 'due_date'):
            loan.due_date = overdue_date
        elif hasattr(loan, 'return_due_date'):
            loan.return_due_date = overdue_date

        fine = lib.calculate_fine(member_id='M001', isbn='ISBN-005')
        assert fine is not None, 'calculate_fine returned None'
        assert float(fine) > 0, f'Overdue fine should be > 0, got {fine}'
        record('fine_for_overdue_return', True)
    except AssertionError as e:
        record('fine_for_overdue_return', False, str(e))
    except (AttributeError, TypeError, NameError) as e:
        record('fine_for_overdue_return', False, f'{type(e).__name__}: {e}')

    # ------------------------------------------------------------------ #
    # 7. Member borrow limit enforcement
    # ------------------------------------------------------------------ #
    try:
        lib = Library('City Library') if 'Library' in dir() else LibraryService()
        member = Member(member_id='M001', name='Alice')
        lib.add_member(member)

        # Get the borrow limit (try common attribute names)
        limit = (
            getattr(lib, 'borrow_limit', None)
            or getattr(member, 'borrow_limit', None)
            or getattr(member, 'max_books', None)
            or 3
        )
        limit = int(limit)

        # Add limit+1 books and borrow limit of them
        for i in range(limit + 1):
            b = Book(isbn=f'LIMIT-{i}', title=f'Book {i}', author='Author')
            lib.add_book(b)
            if i < limit:
                lib.borrow(member_id='M001', isbn=f'LIMIT-{i}')

        # Borrowing one more should fail
        result = None
        try:
            result = lib.borrow(member_id='M001', isbn=f'LIMIT-{limit}')
        except Exception:
            result = None
        assert result is None or result is False, \
            f'Member should not be able to borrow more than {limit} books'
        record('borrow_limit_enforced', True)
    except AssertionError as e:
        record('borrow_limit_enforced', False, str(e))
    except (AttributeError, TypeError, NameError) as e:
        record('borrow_limit_enforced', False, f'{type(e).__name__}: {e}')

    # ------------------------------------------------------------------ #
    # 8. Search books by author
    # ------------------------------------------------------------------ #
    try:
        lib = Library('City Library') if 'Library' in dir() else LibraryService()
        b1 = Book(isbn='ISBN-A1', title='Book A', author='Robert Martin')
        b2 = Book(isbn='ISBN-A2', title='Book B', author='Robert Martin')
        b3 = Book(isbn='ISBN-A3', title='Book C', author='Kent Beck')
        lib.add_book(b1)
        lib.add_book(b2)
        lib.add_book(b3)
        found = lib.search_by_author('Robert Martin')
        assert found is not None, 'search_by_author returned None'
        assert len(found) == 2, f'Expected 2 books by Robert Martin, got {len(found)}'
        record('search_by_author', True)
    except AssertionError as e:
        record('search_by_author', False, str(e))
    except (AttributeError, TypeError, NameError) as e:
        record('search_by_author', False, f'{type(e).__name__}: {e}')

    return results
