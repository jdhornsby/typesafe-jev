"""Ways to show Jev the position. `prose_1` and `json_1` describe the board
plainly; the rest are the raw representations from earlier attempts."""

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


def san_history(board: chess.Board, history: list[str]) -> str:
    return " ".join(history) if history else "(no moves yet)"


def ascii_board(board: chess.Board, history: list[str]) -> str:
    turn = "White" if board.turn == chess.WHITE else "Black"
    return f"{board}\n\n{turn} to move."


def fen(board: chess.Board, history: list[str]) -> str:
    return board.fen()


def pgn_full(board: chess.Board, history: list[str]) -> str:
    def movetext(anchor: chess.Board, moves: list[str]) -> str:
        tokens: list[str] = []
        n = anchor.fullmove_number
        i = 0
        if moves and anchor.turn == chess.BLACK:
            tokens.append(f"{n}... {moves[0]}")
            i, n = 1, n + 1
        while i < len(moves):
            pair = moves[i:i + 2]
            tokens.append(f"{n}. {' '.join(pair)}")
            n += len(pair) // 2
            i += len(pair)
        if board.turn == chess.WHITE:  # bare trailing number cues White
            tokens.append(f"{n}.")
        return " ".join(tokens)

    return movetext(chess.Board(), history)


def pgn_windowed(board: chess.Board, history: list[str]) -> str:
    window = 10

    def movetext(anchor: chess.Board, moves: list[str]) -> str:
        tokens: list[str] = []
        n = anchor.fullmove_number
        i = 0
        if moves and anchor.turn == chess.BLACK:
            tokens.append(f"{n}... {moves[0]}")
            i, n = 1, n + 1
        while i < len(moves):
            pair = moves[i:i + 2]
            tokens.append(f"{n}. {' '.join(pair)}")
            n += len(pair) // 2
            i += len(pair)
        if board.turn == chess.WHITE:  # bare trailing number cues White
            tokens.append(f"{n}.")
        return " ".join(tokens)

    cut = max(0, len(history) - window * 2)
    anchor = chess.Board()
    for move in history[:cut]:
        anchor.push_san(move)
    header = f'[SetUp "1"]\n[FEN "{anchor.fen()}"]\n\n' if cut else ""
    return header + movetext(anchor, history[cut:])


def prose_1(board: chess.Board, history: list[str]) -> str:
    def join(items: list[str]) -> str:
        if len(items) == 1:
            return items[0]
        if len(items) == 2:
            return f"{items[0]} and {items[1]}"
        return ", ".join(items[:-1]) + f", and {items[-1]}"

    def side(colour: chess.Color) -> str:
        groups: list[str] = []
        for piece_type in _PIECE_ORDER:
            ordered = sorted(board.pieces(piece_type, colour),
                             key=lambda s: (chess.square_file(s), chess.square_rank(s)))
            squares = [chess.square_name(s) for s in ordered]
            if not squares:
                continue
            singular, plural = PIECE_NAMES[piece_type]
            groups.append(f"a {singular} on {squares[0]}" if len(squares) == 1
                          else f"{plural} on {join(squares)}")
        return join(groups)

    mover = "White" if board.turn == chess.WHITE else "Black"
    return (
        f"It is {mover}'s turn to move.\n\n"
        f"White has {side(chess.WHITE)}.\n\n"
        f"Black has {side(chess.BLACK)}."
    )


def json_1(board: chess.Board, history: list[str]) -> dict[str, object]:
    def squares(colour: chess.Color) -> dict[str, str]:
        placed: dict[str, str] = {}
        for piece_type in _PIECE_ORDER:
            for square in sorted(board.pieces(piece_type, colour),
                                 key=lambda s: (chess.square_file(s), chess.square_rank(s))):
                placed[chess.square_name(square)] = PIECE_NAMES[piece_type][0]
        return placed

    return {
        "turn": "white" if board.turn == chess.WHITE else "black",
        "white": squares(chess.WHITE),
        "black": squares(chess.BLACK),
    }


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


STATES = {
    "san": san_history,
    "ascii": ascii_board,
    "fen": fen,
    "pgn_full": pgn_full,
    "pgn_windowed": pgn_windowed,
    "prose_1": prose_1,
    "json_1": json_1,
}
