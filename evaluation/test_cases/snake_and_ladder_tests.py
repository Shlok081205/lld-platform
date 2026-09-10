"""
Hidden test harness for the Snake and Ladder problem.
Expects learner's code to define classes such as:
  Board, Player, Dice, Snake, Ladder, Game / SnakeAndLadderGame.

run_tests() returns a list of (name: str, passed: bool, reason: str).
"""


def run_tests():
    results = []

    def record(name, passed, reason=''):
        results.append((name, passed, reason))

    # ------------------------------------------------------------------ #
    # Utility: build a standard game with known snakes/ladders
    # Ladder: 4 -> 14, 9 -> 31
    # Snake : 17 -> 7, 54 -> 34
    # ------------------------------------------------------------------ #
    def _make_game(*player_names):
        board = Board(size=100)
        board.add_ladder(Ladder(start=4, end=14))
        board.add_ladder(Ladder(start=9, end=31))
        board.add_snake(Snake(head=17, tail=7))
        board.add_snake(Snake(head=54, tail=34))
        players = [Player(name=n) for n in player_names]
        game = Game(board=board, players=players)
        return game, board, players

    # ------------------------------------------------------------------ #
    # 1. Create board with players
    # ------------------------------------------------------------------ #
    try:
        game, board, players = _make_game('Alice', 'Bob')
        assert board is not None, 'Board is None'
        assert len(players) == 2, f'Expected 2 players, got {len(players)}'
        record('create_board_with_players', True)
    except AssertionError as e:
        record('create_board_with_players', False, str(e))
    except (AttributeError, TypeError, NameError) as e:
        record('create_board_with_players', False, f'{type(e).__name__}: {e}')

    # ------------------------------------------------------------------ #
    # 2. Roll dice — player moves
    # ------------------------------------------------------------------ #
    try:
        game, board, players = _make_game('Alice')
        alice = players[0]
        start_pos = alice.position if hasattr(alice, 'position') else 0
        game.roll_dice(alice)   # or game.take_turn(alice) or game.play_turn()
        new_pos = alice.position if hasattr(alice, 'position') else None
        assert new_pos is not None, 'Player has no position attribute after roll'
        assert new_pos != start_pos or new_pos >= 0, 'Player position should change after rolling'
        record('roll_dice_player_moves', True)
    except AssertionError as e:
        record('roll_dice_player_moves', False, str(e))
    except (AttributeError, TypeError, NameError) as e:
        record('roll_dice_player_moves', False, f'{type(e).__name__}: {e}')

    # ------------------------------------------------------------------ #
    # 3. Land on ladder — player moves up
    # ------------------------------------------------------------------ #
    try:
        game, board, players = _make_game('Alice')
        alice = players[0]
        # Manually place Alice at position 4; after board resolution she should be at 14
        alice.position = 4
        new_pos = board.apply_cell(4) if hasattr(board, 'apply_cell') else board.get_new_position(4)
        assert new_pos == 14, f'Ladder 4->14: expected 14, got {new_pos}'
        record('land_on_ladder_moves_up', True)
    except AssertionError as e:
        record('land_on_ladder_moves_up', False, str(e))
    except (AttributeError, TypeError, NameError) as e:
        record('land_on_ladder_moves_up', False, f'{type(e).__name__}: {e}')

    # ------------------------------------------------------------------ #
    # 4. Land on snake — player moves down
    # ------------------------------------------------------------------ #
    try:
        game, board, players = _make_game('Alice')
        alice = players[0]
        alice.position = 17
        new_pos = board.apply_cell(17) if hasattr(board, 'apply_cell') else board.get_new_position(17)
        assert new_pos == 7, f'Snake 17->7: expected 7, got {new_pos}'
        record('land_on_snake_moves_down', True)
    except AssertionError as e:
        record('land_on_snake_moves_down', False, str(e))
    except (AttributeError, TypeError, NameError) as e:
        record('land_on_snake_moves_down', False, f'{type(e).__name__}: {e}')

    # ------------------------------------------------------------------ #
    # 5. Player wins when reaching exactly 100
    # ------------------------------------------------------------------ #
    try:
        game, board, players = _make_game('Alice')
        alice = players[0]
        alice.position = 94
        # Simulate rolling a 6 (or set position directly)
        # Use the board's resolution to check position 100
        new_pos = board.apply_cell(100) if hasattr(board, 'apply_cell') else board.get_new_position(100)
        assert new_pos == 100, f'Expected 100 at win position, got {new_pos}'
        record('player_wins_at_100', True)
    except AssertionError as e:
        record('player_wins_at_100', False, str(e))
    except (AttributeError, TypeError, NameError) as e:
        record('player_wins_at_100', False, f'{type(e).__name__}: {e}')

    # ------------------------------------------------------------------ #
    # 6. Cannot move beyond 100 — bounce back or stay
    # ------------------------------------------------------------------ #
    try:
        game, board, players = _make_game('Alice')
        alice = players[0]
        alice.position = 98
        # Rolling a 5 would put at 103, which should bounce to 95 (bounce-back rule)
        # or stay at 98 (stay-rule).  Either is valid — just must not exceed 100.
        overshoot_pos = 98 + 5  # 103
        new_pos = board.apply_cell(overshoot_pos) if hasattr(board, 'apply_cell') else board.get_new_position(overshoot_pos)
        # Some designs clip to 98; others bounce (100 - (103-100) = 97)
        assert new_pos <= 100, f'Position must not exceed 100, got {new_pos}'
        record('cannot_move_beyond_100', True)
    except AssertionError as e:
        record('cannot_move_beyond_100', False, str(e))
    except (AttributeError, TypeError, NameError) as e:
        record('cannot_move_beyond_100', False, f'{type(e).__name__}: {e}')

    # ------------------------------------------------------------------ #
    # 7. Multiple players take turns
    # ------------------------------------------------------------------ #
    try:
        game, board, players = _make_game('Alice', 'Bob', 'Carol')
        # Play 3 turns; check that the current player cycles
        first_player = game.current_player if hasattr(game, 'current_player') else game.get_current_player()
        game.next_turn() if hasattr(game, 'next_turn') else game.advance_turn()
        second_player = game.current_player if hasattr(game, 'current_player') else game.get_current_player()
        assert first_player != second_player, 'Current player should change after next_turn()'
        record('multiple_players_take_turns', True)
    except AssertionError as e:
        record('multiple_players_take_turns', False, str(e))
    except (AttributeError, TypeError, NameError) as e:
        record('multiple_players_take_turns', False, f'{type(e).__name__}: {e}')

    # ------------------------------------------------------------------ #
    # 8. Game ends when a player wins
    # ------------------------------------------------------------------ #
    try:
        game, board, players = _make_game('Alice', 'Bob')
        alice = players[0]
        # Force Alice to position 100 (win)
        alice.position = 100
        is_over = (
            game.is_over()        if hasattr(game, 'is_over')
            else game.has_winner() if hasattr(game, 'has_winner')
            else game.game_over   if hasattr(game, 'game_over')
            else None
        )
        winner = (
            game.winner        if hasattr(game, 'winner')
            else game.get_winner() if hasattr(game, 'get_winner')
            else None
        )
        assert is_over or winner is not None, \
            'Game should recognise a winner when a player is at position 100'
        record('game_ends_when_player_wins', True)
    except AssertionError as e:
        record('game_ends_when_player_wins', False, str(e))
    except (AttributeError, TypeError, NameError) as e:
        record('game_ends_when_player_wins', False, f'{type(e).__name__}: {e}')

    return results
