"""Judge autoregressive-schemas levels with jev."""

import asyncio
import json
import statistics as st
import time
from collections import defaultdict
from pathlib import Path

from dotenv import load_dotenv
from typesafe_sdk import AsyncTypeSafeClient, RetryPolicy

from . import rubric
from ..select import base_parser
from ..trace import Tracer

DATA = Path(__file__).resolve().parents[3] / "data" / "autoregressive_schemas"
NO_RETRY = RetryPolicy(max_retries=0)
MAX_RETRIES = 8
BACKOFF_MAX = 5.0


def _load_items(condition: str) -> list[dict]:
    items = []
    for gen_path in sorted((DATA / "generations").glob(f"{condition}_*.json")):
        source = gen_path.stem
        likert_path = DATA / "judgments" / "likert" / f"{source}.json"
        reach_path = DATA / "judgments" / "reachability" / f"reachability_{source}.json"
        likert = json.loads(likert_path.read_text()) if likert_path.exists() else None
        reach = json.loads(reach_path.read_text()) if reach_path.exists() else None
        for i, gen in enumerate(json.loads(gen_path.read_text())):
            items.append({
                "source": source, "index": i, "case": gen["case"], "level": gen["level"],
                "original_scores": likert[i]["judgment"]["scores"] if likert else None,
                "original_satisfied": [e["satisfied"] for e in reach[i]["encounters"]] if reach else None,
            })
    return items


def _recorded(path: Path) -> set[tuple[str, int]]:
    if not path.exists():
        return set()
    with path.open() as f:
        return {(r["source"], r["index"]) for r in map(json.loads, f)}


async def _call(client, state, model, questions):
    """Return (response, latency_seconds, retries)."""
    delay = 0.5
    for retries in range(MAX_RETRIES + 1):
        try:
            start = time.monotonic()
            response = await client.system_one(state=state, model=model, questions=questions)
            return response, time.monotonic() - start, retries
        except Exception:
            if retries == MAX_RETRIES:
                raise
            await asyncio.sleep(min(delay, BACKOFF_MAX))
            delay *= 2


async def _gather(todo: list[dict], args, tracer: Tracer) -> None:
    sem = asyncio.Semaphore(args.concurrency)
    done = 0

    async with AsyncTypeSafeClient(retry=NO_RETRY) as client:
        async def worker(item: dict) -> None:
            nonlocal done
            questions = {**rubric.likert_questions(), **rubric.reachability_questions(item["level"])}
            state = rubric.build_state(item["case"], item["level"])
            async with sem:
                try:
                    response, latency, retries = await _call(client, state, args.model, questions)
                except Exception as e:
                    print(f"  {item['source']}[{item['index']}] failed, retry on resume: {e}")
                    return
            tracer.record(
                source=item["source"], index=item["index"], case=item["case"],
                latency=round(latency, 3), retries=retries,
                jev_scores={name: {"score": a.score, "confidence": a.confidence}
                            for name, a in response.scores.items()},
                jev_satisfied={name: a.noul for name, a in response.nouls.items()},
                original_scores=item["original_scores"], original_satisfied=item["original_satisfied"],
            )
            done += 1
            if done % 20 == 0:
                print(f"  {done}/{len(todo)}", flush=True)

        await asyncio.gather(*(worker(item) for item in todo))


def _summarize(path: Path) -> None:
    score_diffs: dict[str, list[float]] = defaultdict(list)
    latencies: list[float] = []
    retries = agree = total = 0
    with path.open() as f:
        for line in f:
            r = json.loads(line)
            latencies.append(r["latency"])
            retries += r["retries"]
            if r["original_scores"]:
                for name, jev in r["jev_scores"].items():
                    score_diffs[name].append((jev["score"] + 1) - r["original_scores"][name]["score"])
            if r["original_satisfied"]:
                for i, original_sat in enumerate(r["original_satisfied"]):
                    total += 1
                    agree += (r["jev_satisfied"][f"encounter_{i}"] > 0.5) == original_sat

    if score_diffs:
        print("\nlikert, mean(jev - original), +ve = jev more lenient:")
        for name, diffs in score_diffs.items():
            print(f"  {name:<22} {st.mean(diffs):+.2f}")
    if total:
        print(f"\nreachability agreement: {agree}/{total} = {agree / total:.1%}")
    if latencies:
        print(f"\nlatency: median {st.median(latencies):.2f}s, max {max(latencies):.2f}s  ({retries} retries)")


def main() -> None:
    load_dotenv()
    parser = base_parser("judge autoregressive-schemas levels with jev")
    parser.add_argument("--condition", default="minimal",
                        help="generation condition to judge, e.g. minimal, gamin, qwen (see data/.../manifest.json)")
    args = parser.parse_args()

    items = _load_items(args.condition)
    if not items:
        raise SystemExit(f"no generations found for condition {args.condition!r}")
    if args.limit:
        items = items[:args.limit]

    run_id = args.run_id or f"{args.condition}-{time.strftime('%Y%m%d-%H%M%S')}"
    path = Path("traces") / "judge" / f"{run_id}.jsonl"

    recorded = _recorded(path)
    todo = [item for item in items if (item["source"], item["index"]) not in recorded]
    print(f"judge: {len(items)} levels ({args.condition}), {len(recorded)} done, {len(todo)} to run")
    print(f"run-id: {run_id}  (resume with --run-id {run_id})")

    if todo:
        tracer = Tracer(path, append=True)
        try:
            asyncio.run(_gather(todo, args, tracer))
        finally:
            tracer.close()

    _summarize(path)


if __name__ == "__main__":
    main()
