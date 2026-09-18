"""Probe Jev's factual knowledge on MMLU. Rerun with the same --run-id to resume."""

import argparse
import asyncio
import json
import statistics as st
import sys
import time
from collections import defaultdict
from pathlib import Path

from datasets import load_dataset
from dotenv import load_dotenv
from typesafe_sdk import AsyncTypeSafeClient, Choice, RetryPolicy

from ..trace import Tracer

TRACE_DIR = Path("traces/knowledge")
RETRY = RetryPolicy(max_retries=8, http_statuses={429, 500, 502, 503, 504}, respect_retry_after=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="jev-latest")
    parser.add_argument("--limit", type=int, default=0, help="first N questions; 0 = all")
    parser.add_argument("--concurrency", type=int, default=8)
    parser.add_argument("--run-id", default="", dest="run_id")
    return parser.parse_args()


def recorded_indices(path: Path) -> set[int]:
    if not path.exists():
        return set()
    with path.open() as f:
        return {json.loads(line)["index"] for line in f}


async def run(rows, todo: list[int], args: argparse.Namespace, tracer: Tracer) -> None:
    sem = asyncio.Semaphore(args.concurrency)
    done = 0
    async with AsyncTypeSafeClient(retry=RETRY) as client:
        async def worker(index: int) -> None:
            nonlocal done
            row = rows[index]
            options = list(row["choices"])
            if len(set(options)) != len(options):
                return
            async with sem:
                try:
                    response = await client.system_one(
                        state=row["question"], model=args.model,
                        questions={"answer": Choice(instructions="Select the correct answer.",
                                                    criteria={o: None for o in options})})
                except Exception as e:
                    print(f"  q{index} failed, will retry on resume: {e}", file=sys.stderr)
                    return
            answer = response.choices["answer"]
            gold = options[row["answer"]]
            tracer.record(index=index, subject=row["subject"], question=row["question"],
                          chosen=answer.choice, gold=gold, correct=answer.choice == gold,
                          confidence=answer.confidence)
            done += 1
            if done % 200 == 0:
                print(f"  {done}/{len(todo)}", flush=True)

        await asyncio.gather(*(worker(i) for i in todo))


def summarize(path: Path) -> None:
    scored: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    conf_right: list[float] = []
    conf_wrong: list[float] = []
    with path.open() as f:
        for line in f:
            r = json.loads(line)
            scored[r["subject"]][0] += int(r["correct"])
            scored[r["subject"]][1] += 1
            (conf_right if r["correct"] else conf_wrong).append(r["confidence"])

    total = sum(t for _, t in scored.values())
    right = sum(c for c, _ in scored.values())
    print(f"\naccuracy: {right}/{total} = {right / total:.1%}")
    if conf_right:
        print(f"confidence when correct: {st.mean(conf_right):.2f}")
    if conf_wrong:
        print(f"confidence when wrong:   {st.mean(conf_wrong):.2f}")
    print("\nby subject:")
    for subject in sorted(scored, key=lambda s: scored[s][0] / scored[s][1]):
        c, t = scored[subject]
        print(f"  {subject:34s} {c:>3}/{t:<3} {c / t:.0%}")


def main() -> None:
    load_dotenv()
    args = parse_args()

    rows = load_dataset("cais/mmlu", "all", split="test")
    if args.limit:
        rows = rows.select(range(args.limit))

    run_id = args.run_id or f"mmlu-{time.strftime('%Y%m%d-%H%M%S')}"
    path = TRACE_DIR / f"{run_id}.jsonl"

    recorded = recorded_indices(path)
    todo = [i for i in range(len(rows)) if i not in recorded]
    print(f"mmlu: {len(rows)} questions, {len(recorded)} already done, {len(todo)} to run")
    print(f"run-id: {run_id}  (resume with --run-id {run_id})")

    if todo:
        tracer = Tracer(path, append=True)
        try:
            asyncio.run(run(rows, todo, args, tracer))
        finally:
            tracer.close()

    summarize(path)


if __name__ == "__main__":
    main()
