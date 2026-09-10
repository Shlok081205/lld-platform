"""
Hidden test harness for the Parking Lot problem.
Expects learner's code to define classes such as:
  ParkingLot, ParkingFloor, ParkingSpot (CarSpot, BikeSpot, HandicappedSpot),
  Vehicle (Car, Motorcycle), Ticket, ParkingLotService / ParkingLotSystem.

run_tests() returns a list of (name: str, passed: bool, reason: str).
"""


def run_tests():
    results = []

    def record(name, passed, reason=''):
        results.append((name, passed, reason))

    # ------------------------------------------------------------------ #
    # 1. Create parking lot with floors and spots
    # ------------------------------------------------------------------ #
    try:
        lot = ParkingLot('lot-1', 'Central Lot')
        floor1 = ParkingFloor(1)
        # Add at least one car spot and one bike spot
        for i in range(3):
            floor1.add_spot(CarSpot(f'C-1-{i}'))
        for i in range(2):
            floor1.add_spot(BikeSpot(f'B-1-{i}'))
        lot.add_floor(floor1)
        assert lot is not None, 'ParkingLot creation returned None'
        record('create_parking_lot', True)
    except AssertionError as e:
        record('create_parking_lot', False, str(e))
    except (AttributeError, TypeError, NameError) as e:
        record('create_parking_lot', False, f'{type(e).__name__}: {e}')

    # ------------------------------------------------------------------ #
    # 2. Park a car — returns ticket
    # ------------------------------------------------------------------ #
    try:
        lot = ParkingLot('lot-1', 'Central Lot')
        floor1 = ParkingFloor(1)
        floor1.add_spot(CarSpot('C-1-0'))
        lot.add_floor(floor1)
        car = Car('KA-01-AB-1234')
        ticket = lot.park(car)
        assert ticket is not None, 'park() returned None — expected a Ticket'
        record('park_car_returns_ticket', True)
    except AssertionError as e:
        record('park_car_returns_ticket', False, str(e))
    except (AttributeError, TypeError, NameError) as e:
        record('park_car_returns_ticket', False, f'{type(e).__name__}: {e}')

    # ------------------------------------------------------------------ #
    # 3. Park a motorcycle
    # ------------------------------------------------------------------ #
    try:
        lot = ParkingLot('lot-1', 'Central Lot')
        floor1 = ParkingFloor(1)
        floor1.add_spot(BikeSpot('B-1-0'))
        lot.add_floor(floor1)
        bike = Motorcycle('KA-01-XY-9999')
        ticket = lot.park(bike)
        assert ticket is not None, 'park(motorcycle) returned None — expected a Ticket'
        record('park_motorcycle', True)
    except AssertionError as e:
        record('park_motorcycle', False, str(e))
    except (AttributeError, TypeError, NameError) as e:
        record('park_motorcycle', False, f'{type(e).__name__}: {e}')

    # ------------------------------------------------------------------ #
    # 4. Parking lot full — cannot park more
    # ------------------------------------------------------------------ #
    try:
        lot = ParkingLot('lot-1', 'Central Lot')
        floor1 = ParkingFloor(1)
        floor1.add_spot(CarSpot('C-1-0'))  # Only 1 spot
        lot.add_floor(floor1)
        car1 = Car('KA-01-AA-0001')
        car2 = Car('KA-01-AA-0002')
        lot.park(car1)
        # Parking the second car should fail (return None, raise exception, or return falsy)
        result = None
        try:
            result = lot.park(car2)
        except Exception:
            result = None
        assert result is None or result is False, \
            f'Expected None/False/exception for full lot, got {result}'
        record('parking_lot_full', True)
    except AssertionError as e:
        record('parking_lot_full', False, str(e))
    except (AttributeError, TypeError, NameError) as e:
        record('parking_lot_full', False, f'{type(e).__name__}: {e}')

    # ------------------------------------------------------------------ #
    # 5. Unpark using ticket — returns fee
    # ------------------------------------------------------------------ #
    try:
        import time as _time
        lot = ParkingLot('lot-1', 'Central Lot')
        floor1 = ParkingFloor(1)
        floor1.add_spot(CarSpot('C-1-0'))
        lot.add_floor(floor1)
        car = Car('KA-01-AB-1234')
        ticket = lot.park(car)
        # Simulate a tiny duration so fee can be computed
        _time.sleep(0.01)
        fee = lot.unpark(ticket)
        assert fee is not None, 'unpark() returned None — expected a fee (float/int)'
        assert float(fee) >= 0, f'Fee should be >= 0, got {fee}'
        record('unpark_returns_fee', True)
    except AssertionError as e:
        record('unpark_returns_fee', False, str(e))
    except (AttributeError, TypeError, NameError) as e:
        record('unpark_returns_fee', False, f'{type(e).__name__}: {e}')

    # ------------------------------------------------------------------ #
    # 6. Spot becomes available after unpark
    # ------------------------------------------------------------------ #
    try:
        lot = ParkingLot('lot-1', 'Central Lot')
        floor1 = ParkingFloor(1)
        floor1.add_spot(CarSpot('C-1-0'))
        lot.add_floor(floor1)
        car1 = Car('KA-01-AA-0001')
        car2 = Car('KA-01-AA-0002')
        ticket = lot.park(car1)
        lot.unpark(ticket)
        # Now lot should have a free spot again
        ticket2 = lot.park(car2)
        assert ticket2 is not None, 'After unpark, parking the next car should succeed'
        record('spot_available_after_unpark', True)
    except AssertionError as e:
        record('spot_available_after_unpark', False, str(e))
    except (AttributeError, TypeError, NameError) as e:
        record('spot_available_after_unpark', False, f'{type(e).__name__}: {e}')

    # ------------------------------------------------------------------ #
    # 7. Different vehicle types use correct spot types
    # ------------------------------------------------------------------ #
    try:
        lot = ParkingLot('lot-1', 'Central Lot')
        floor1 = ParkingFloor(1)
        floor1.add_spot(BikeSpot('B-1-0'))   # Only a bike spot — no car spot
        lot.add_floor(floor1)
        car = Car('KA-01-AB-0001')
        # Car must NOT park in a bike spot
        result = None
        try:
            result = lot.park(car)
        except Exception:
            result = None
        assert result is None or result is False, \
            'Car should not park in a BikeSpot-only lot'
        record('vehicle_uses_correct_spot_type', True)
    except AssertionError as e:
        record('vehicle_uses_correct_spot_type', False, str(e))
    except (AttributeError, TypeError, NameError) as e:
        record('vehicle_uses_correct_spot_type', False, f'{type(e).__name__}: {e}')

    # ------------------------------------------------------------------ #
    # 8. Handicapped spot support
    # ------------------------------------------------------------------ #
    try:
        lot = ParkingLot('lot-1', 'Central Lot')
        floor1 = ParkingFloor(1)
        floor1.add_spot(HandicappedSpot('H-1-0'))
        lot.add_floor(floor1)
        # A Car (or HandicappedVehicle) should be able to park in a HandicappedSpot
        vehicle = Car('KA-01-HC-0001') if 'HandicappedVehicle' not in dir() else HandicappedVehicle('KA-01-HC-0001')
        ticket = lot.park(vehicle)
        # Just assert no crash; some designs may return None for non-handicapped cars
        record('handicapped_spot_support', True)
    except (AttributeError, TypeError, NameError) as e:
        record('handicapped_spot_support', False, f'{type(e).__name__}: {e}')
    except Exception as e:
        record('handicapped_spot_support', False, f'Unexpected: {e}')

    return results
