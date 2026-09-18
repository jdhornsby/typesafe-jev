# jev plays chess

Jev plays chess against itself.

## Setup

```
uv sync
cp .env.sample .env   # add TYPESAFE_API_KEY
```

## Run

```
uv run jev-plays-chess
```

## Vs Stockfish

Needs the `stockfish` binary (`brew install stockfish`). Jev plays white; options pass straight through.

```
uv run jev-plays-chess --opponent stockfish
uv run jev-plays-chess --opponent stockfish \
  --stockfish-option UCI_LimitStrength=true --stockfish-option UCI_Elo=1500
uv run jev-plays-chess --opponent stockfish \
  --stockfish-option "Skill Level=0" --stockfish-movetime 0.001
```
