# jev plays chess

Jev plays chess against itself.

## Setup

```
uv sync
cp .env.sample .env   # add TYPESAFE_API_KEY   (needs the stockfish binary: brew install stockfish)
```

## Run

```
uv run jev-plays-chess --state san           --opponent stockfish --stockfish-option UCI_LimitStrength=true --stockfish-option UCI_Elo=1320 --max-plies 30 --run-id char-san
uv run jev-plays-chess --state ascii         --opponent stockfish --stockfish-option UCI_LimitStrength=true --stockfish-option UCI_Elo=1320 --max-plies 30 --run-id char-ascii
uv run jev-plays-chess --state fen           --opponent stockfish --stockfish-option UCI_LimitStrength=true --stockfish-option UCI_Elo=1320 --max-plies 30 --run-id char-fen
uv run jev-plays-chess --state pgn_full      --opponent stockfish --stockfish-option UCI_LimitStrength=true --stockfish-option UCI_Elo=1320 --max-plies 30 --run-id char-pgn_full
uv run jev-plays-chess --state pgn_windowed  --opponent stockfish --stockfish-option UCI_LimitStrength=true --stockfish-option UCI_Elo=1320 --max-plies 30 --run-id char-pgn_windowed
uv run jev-plays-chess --state prose_1       --opponent stockfish --stockfish-option UCI_LimitStrength=true --stockfish-option UCI_Elo=1320 --max-plies 30 --run-id char-prose_1
uv run jev-plays-chess --state json_1        --opponent stockfish --stockfish-option UCI_LimitStrength=true --stockfish-option UCI_Elo=1320 --max-plies 30 --run-id char-json_1
```

### Results

Jev per-move confidence, one 30-ply game each vs Stockfish (UCI_Elo 1320):

| state | moves | mean | median | min | max |
|---|--:|--:|--:|--:|--:|
| san | 12 | 0.25 | 0.23 | 0.06 | 1.00 |
| ascii | 13 | 0.18 | 0.07 | 0.04 | 1.00 |
| fen | 15 | 0.18 | 0.14 | 0.03 | 0.57 |
| pgn_full | 15 | 0.19 | 0.10 | 0.05 | 0.56 |
| pgn_windowed | 15 | 0.22 | 0.20 | 0.04 | 0.55 |
| prose_1 | 15 | 0.29 | 0.30 | 0.08 | 0.54 |
| json_1 | 15 | 0.26 | 0.23 | 0.08 | 0.79 |
