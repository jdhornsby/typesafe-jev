"""Ask Jev a choice per item, score against gold. Async, resumable by --run-id."""

import argparse
import asyncio
import json
import statistics as st
import sys
import time
from collections import defaultdict
from pathlib import Path

from dotenv import load_dotenv
from typesafe_sdk import AsyncTypeSafeClient, Choice, RetryPolicy

from .trace import Tracer

RETRY = RetryPolicy(max_retries=8, http_statuses={429, 500, 502, 503, 504}, respect_retry_after=True)


def base_parser(description: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--model", default="jev-latest")
    parser.add_argument("--limit", type=int, default=0, help="first N items; 0 = all")
    parser.add_argument("--concurrency", type=int, default=12)
    parser.add_argument("--run-id", default="", dest="run_id")
    return parser


def _recorded(path: Path) -> set[int]:
    if not path.exists():
        return set()
    with path.open() as f:
        return {json.loads(line)["index"] for line in f}


async def _gather(items, todo, instructions, args, tracer):
    sem = asyncio.Semaphore(args.concurrency)
    done = 0
    async with AsyncTypeSafeClient(retry=RETRY) as client:
        async def worker(i):
            nonlocal done
            item = items[i]
            options = item["options"]
            if len(set(options)) != len(options):
                return
            async with sem:
                try:
                    response = await client.system_one(
                        state=item["state"], model=args.model,
                        questions={"answer": Choice(instructions=instructions,
                                                    criteria={o: None for o in options})})
                except Exception as e:
                    print(f"  {i} failed, retry on resume: {e}", file=sys.stderr)
                    return
            answer = response.choices["answer"]
            tracer.record(index=i, group=item.get("group", ""), chosen=answer.choice,
                          gold=item["gold"], correct=answer.choice == item["gold"],
                          confidence=answer.confidence)
            done += 1
            if done % 200 == 0:
                print(f"  {done}/{len(todo)}", flush=True)

        await asyncio.gather(*(worker(i) for i in todo))


def _summarize(path: Path) -> None:
    groups: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    conf_right: list[float] = []
    conf_wrong: list[float] = []
    with path.open() as f:
        for line in f:
            r = json.loads(line)
            groups[r["group"]][0] += int(r["correct"])
            groups[r["group"]][1] += 1
            (conf_right if r["correct"] else conf_wrong).append(r["confidence"])

    total = sum(t for _, t in groups.values())
    right = sum(c for c, _ in groups.values())
    print(f"\naccuracy: {right}/{total} = {right / total:.1%}")
    if conf_right:
        print(f"confidence when correct: {st.mean(conf_right):.2f}")
    if conf_wrong:
        print(f"confidence when wrong:   {st.mean(conf_wrong):.2f}")
    named = [g for g in groups if g]
    if named:
        print("\nby group:")
        for g in sorted(named, key=lambda g: groups[g][0] / groups[g][1]):
            c, t = groups[g]
            print(f"  {g:36s} {c:>4}/{t:<4} {c / t:.0%}")


def run(name: str, items: list[dict], instructions: str, args: argparse.Namespace) -> None:
    load_dotenv()
    if args.limit:
        items = items[:args.limit]
    run_id = args.run_id or f"{name}-{time.strftime('%Y%m%d-%H%M%S')}"
    path = Path("traces") / name / f"{run_id}.jsonl"

    recorded = _recorded(path)
    todo = [i for i in range(len(items)) if i not in recorded]
    print(f"{name}: {len(items)} items, {len(recorded)} done, {len(todo)} to run")
    print(f"run-id: {run_id}  (resume with --run-id {run_id})")

    if todo:
        tracer = Tracer(path, append=True)
        try:
            asyncio.run(_gather(items, todo, instructions, args, tracer))
        finally:
            tracer.close()

    _summarize(path)
