"""banking77: route a customer query to its intent."""

from datasets import load_dataset

from ..select import base_parser, run


def main() -> None:
    args = base_parser("route banking queries to intents (banking77)").parse_args()
    rows = load_dataset("mteb/banking77", split="test")
    options = sorted({r["label_text"].replace("_", " ") for r in rows})
    items = [{"state": r["text"], "options": options,
              "gold": r["label_text"].replace("_", " "), "group": ""} for r in rows]
    run("routing", items, "Which category best matches the request?", args)
