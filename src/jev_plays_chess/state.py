"""Describes a chess position and its moves in plain language for Jev."""

import chess

# (singular, plural)
PIECE_NAMES = {
    chess.PAWN: ("pawn", "pawns"),
    chess.KNIGHT: ("knight", "knights"),
    chess.BISHOP: ("bishop", "bishops"),
    chess.ROOK: ("rook", "rooks"),
    chess.QUEEN: ("queen", "queens"),
    chess.KING: ("king", "kings"),
}

_PIECE_ORDER = [chess.KING, chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT, chess.PAWN]


def _join(items: list[str]) -> str:
    """'a', 'a and b', 'a, b and c'."""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return ", ".join(items[:-1]) + f", and {items[-1]}"


def _side(board: chess.Board, colour: chess.Color) -> str:
    groups: list[str] = []
    for piece_type in _PIECE_ORDER:
        ordered = sorted(board.pieces(piece_type, colour),
                         key=lambda s: (chess.square_file(s), chess.square_rank(s)))
        squares = [chess.square_name(s) for s in ordered]
        if not squares:
            continue
        singular, plural = PIECE_NAMES[piece_type]
        if len(squares) == 1:
            groups.append(f"a {singular} on {squares[0]}")
        else:
            groups.append(f"{plural} on {_join(squares)}")
    return _join(groups)


def describe_board(board: chess.Board) -> str:
    mover = "White" if board.turn == chess.WHITE else "Black"
    return (
        f"It is {mover}'s turn to move.\n\n"
        f"White has {_side(board, chess.WHITE)}.\n\n"
        f"Black has {_side(board, chess.BLACK)}."
    )


def describe_move(board: chess.Board, move: chess.Move) -> str:
    piece = board.piece_at(move.from_square)
    assert piece is not None
    frm, to = chess.square_name(move.from_square), chess.square_name(move.to_square)
    name = PIECE_NAMES[piece.piece_type][0]

    if board.is_castling(move):
        side = "kingside" if chess.square_file(move.to_square) == 6 else "queenside"
        desc = f"The king castles {side}"
    elif board.is_en_passant(move):
        desc = f"The pawn on {frm} captures en passant, landing on {to}"
    elif board.is_capture(move):
        captured = board.piece_at(move.to_square)
        assert captured is not None
        desc = f"The {name} on {frm} takes the {PIECE_NAMES[captured.piece_type][0]} on {to}"
    else:
        desc = f"The {name} on {frm} moves to {to}"

    if move.promotion:
        desc += f", promoting to a {PIECE_NAMES[move.promotion][0]}"
    if board.gives_check(move):
        desc += ", with check"
    return desc
