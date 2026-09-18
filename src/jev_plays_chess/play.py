"""Jev plays chess, choosing each move via the choice API."""

import argparse
import time
from pathlib import Path

import chess
import chess.engine
import chess.pgn
import chess.svg
from dotenv import load_dotenv
from typesafe_sdk import Choice, TypeSafeClient

from .state import describe_board, describe_move
from .trace import Tracer

INSTRUCTIONS = "Choose the best move for the side to move in this chess position."


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="jev-latest")
    parser.add_argument("--opponent", choices=["self", "stockfish"], default="self",
                        help="jev plays white; this is who plays black")
    parser.add_argument("--stockfish-option", action="append", default=[], metavar="NAME=VALUE",
                        dest="stockfish_options", help="passed through to stockfish; repeatable")
    parser.add_argument("--stockfish-movetime", type=float, default=0.1, dest="stockfish_movetime")
    parser.add_argument("--max-plies", type=int, default=200, dest="max_plies")
    parser.add_argument("--run-id", default="", dest="run_id")
    return parser.parse_args()


def get_move(client: TypeSafeClient, model: str,
             board: chess.Board) -> tuple[str, dict[str, float], float]:
    """Returns (move, probabilities, confidence)."""
    criteria = {board.san(move): describe_move(board, move) for move in board.legal_moves}
    response = client.system_one(
        state=describe_board(board),
        model=model,
        questions={"move": Choice(instructions=INSTRUCTIONS, criteria=criteria)},
    )
    answer = response.choices["move"]
    return answer.choice, answer.probabilities, answer.confidence


def render(board: chess.Board, path: Path) -> None:
    last = board.move_stack[-1] if board.move_stack else None
    path.write_text(chess.svg.board(board, lastmove=last))


def _value(text: str) -> str | int | bool:
    if text.lower() in ("true", "false"):
        return text.lower() == "true"
    try:
        return int(text)
    except ValueError:
        return text


def play(client, args, engine, limit, run_id: str, tracer: Tracer) -> None:
    board = chess.Board()
    frames = Path("traces") / run_id
    frames.mkdir(parents=True, exist_ok=True)
    render(board, frames / "000-start.svg")

    black = "jev" if engine is None else "stockfish"
    print(f"Executing game: jev (white) vs {black} (black)")

    while not board.is_game_over(claim_draw=True) and board.ply() < args.max_plies:
        colour = "w" if board.turn == chess.WHITE else "b"
        number = board.fullmove_number

        if engine is None or board.turn == chess.WHITE:
            move, probabilities, confidence = get_move(client, args.model, board)
            board.push_san(move)
            tracer.record(ply=board.ply(), colour=colour, move=move,
                          probabilities=probabilities, confidence=confidence)
            note = f"(confidence {confidence:.2f})"
        else:
            result = engine.play(board, limit)
            move = board.san(result.move)
            board.push(result.move)
            tracer.record(ply=board.ply(), colour=colour, move=move)
            note = "(stockfish)"

        render(board, frames / f"{board.ply():03d}-{move}.svg")
        print(f"{number:>3}. {colour}  {move}   {note}")

    game = chess.pgn.Game.from_board(board)
    game.headers["White"] = "jev"
    game.headers["Black"] = black
    pgn_path = Path("traces") / f"{run_id}.pgn"
    pgn_path.write_text(str(game) + "\n")

    print(f"result: {board.result(claim_draw=True)} ({board.ply()} plies)")
    print(f"pgn: {pgn_path}")
    print(f"frames: {frames}")


def main() -> None:
    load_dotenv()
    args = parse_args()
    run_id = args.run_id or time.strftime("%Y%m%d-%H%M%S")
    tracer = Tracer(f"traces/{run_id}.jsonl")

    engine = limit = None
    if args.opponent == "stockfish":
        engine = chess.engine.SimpleEngine.popen_uci("stockfish")
        options = dict(option.split("=", 1) for option in args.stockfish_options)
        engine.configure({name: _value(value) for name, value in options.items()})
        limit = chess.engine.Limit(time=args.stockfish_movetime)

    try:
        with TypeSafeClient() as client:
            play(client, args, engine, limit, run_id, tracer)
    finally:
        tracer.close()
        if engine is not None:
            engine.quit()


if __name__ == "__main__":
    main()
