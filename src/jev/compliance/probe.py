"""LegalBench: classify text against the task's rule."""

from datasets import load_dataset

from ..select import base_parser, run

RULES = {
    "hearsay": "Hearsay is an out-of-court statement introduced to prove the truth of "
               "the matter asserted. Is there hearsay?",
}


def main() -> None:
    parser = base_parser("classify a LegalBench task against its rule")
    parser.add_argument("--task", default="hearsay", choices=list(RULES))
    args = parser.parse_args()
    rows = load_dataset("nguha/legalbench", args.task, split="test")
    options = sorted({r["answer"] for r in rows})
    items = [{"state": r["text"], "options": options, "gold": r["answer"],
              "group": r.get("slice", "")} for r in rows]
    run("compliance", items, RULES[args.task], args)
