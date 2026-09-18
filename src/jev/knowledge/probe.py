"""MMLU: Jev's factual knowledge."""

from datasets import load_dataset

from ..select import base_parser, run


def main() -> None:
    args = base_parser("probe Jev's knowledge on MMLU").parse_args()
    rows = load_dataset("cais/mmlu", "all", split="test")
    items = [{"state": r["question"], "options": list(r["choices"]),
              "gold": r["choices"][r["answer"]], "group": r["subject"]} for r in rows]
    run("knowledge", items, "Select the correct answer.", args)
