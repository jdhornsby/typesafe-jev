"""Judge rubric - adapted from the source judge prompts but adjusted to fit Jev"""

from typesafe_sdk import Noul, Score

# Likert rubric

LIKERT_CONTEXT = (
    "You are a strict judge evaluating an AI-generated game level configuration "
    "(`output`), generated for the given `input` (genre, mood, player class, "
    "target difficulty). The level is a functional game configuration -- the "
    "fields are the product, and must work together as a coherent, playable "
    "level, as if loaded into a game engine.\n\n"
    "Scoring discipline: the top of each rubric means flawless. The middle "
    "means mediocre -- real problems that a designer would flag. Do not round "
    "up; if unsure between two levels, pick the lower one. Most levels should "
    "land in the middle of each rubric, not at the top."
)

LIKERT_QUESTIONS = {
    "reference_integrity": "Do cross-references resolve by exact name?",
    "causal_chain": "Does each encounter's trigger logically and specifically set up the next encounter or the boss fight?",
    "balance": "Are the numbers internally consistent?",
    "thematic_coherence": "Do all named elements belong in the same world?",
    "mechanical_sense": "Do pickup effects and enemy weaknesses have a logical functional connection?",
    "completeness": "Are all fields specific and non-redundant?",
}

LIKERT_CRITERIA = {
    "reference_integrity": [
        "References are generic or disconnected. Weaknesses don't correspond to anything in the level.",
        "Two or more broken references. Boss weakness doesn't match any pickup.",
        "One reference points to something that doesn't exist or uses a description instead of a name (\"fire magic\" instead of \"Flame Staff\").",
        "One reference uses a minor variation (e.g., \"the Ember Shard\" vs \"Ember Shard\") but all are identifiable.",
        "Every weakness and the boss victory_condition reference items by exact name. Zero mismatches.",
    ],
    "causal_chain": [
        "Triggers are placeholder text or completely disconnected from the level structure.",
        "One or more triggers have no logical connection to the next encounter's location or situation.",
        "Triggers exist but are generic (\"the path opens,\" \"proceed to next area\"). Encounters could be reordered.",
        "Two triggers are specific and causal. One is weaker but still connected.",
        "All three triggers are specific physical or narrative consequences that make the next encounter inevitable. Removing any encounter would break the chain.",
    ],
    "balance": [
        "Numbers are incoherent. Player cannot survive, or encounters are trivially easy for a \"brutal\" difficulty.",
        "Multiple inversions. Boss stats are comparable to or weaker than encounter enemies. Numbers feel random.",
        "One clear inversion in escalation (e.g., encounter 2 enemy is weaker than encounter 1). Or difficulty label doesn't match the numbers.",
        "Stats generally escalate with one minor inversion. Boss is harder than encounters. Difficulty is reasonable.",
        "All stats escalate monotonically. Boss is clearly the hardest. Difficulty matches the target. Numbers are tight and intentional.",
    ],
    "thematic_coherence": [
        "No coherent theme. Elements feel randomly generated.",
        "Two or more elements clash with the theme. A sci-fi enemy in a fantasy level, or a \"serene\" level with violent imagery.",
        "Theme is present but some elements are generic placeholders that could belong to any level (\"Dark Chamber,\" \"Ancient Relic\").",
        "Strong theme with one element that's slightly generic or off-tone.",
        "Every element reinforces the theme and mood. Nothing feels out of place. A designer would ship this theme package.",
    ],
    "mechanical_sense": [
        "Weaknesses appear randomly assigned to pickups with no functional logic.",
        "Two or more nonsensical connections.",
        "One connection is nonsensical (movement speed boots as a combat weakness, a defensive item as an offensive weakness).",
        "Most connections are logical. One is a stretch but defensible.",
        "Every pickup-weakness pair has an obvious, logical connection. A fire flask melts an ice enemy. An amulet of light damages a shadow creature.",
    ],
    "completeness": [
        "Fields are obviously placeholder text or heavily repeated.",
        "Multiple fields feel like filler. Several encounters share similar descriptions.",
        "Two or more generic fields, or noticeable repetition across encounters.",
        "One minor repetition or one slightly generic field.",
        "Every field is specific, distinct, and adds unique information. No two encounters share locations, enemy types, or hazard descriptions.",
    ],
}


def likert_questions() -> dict[str, Score]:
    return {name: Score(instructions=LIKERT_QUESTIONS[name], criteria=list(levels))
            for name, levels in LIKERT_CRITERIA.items()}


# Reachability judge

REACHABILITY_CONTEXT = (
    "The player fights `output.encounters` in order, starting with only "
    "`output.player_weapon`. Pickups are NOT available during the encounter "
    "they appear in -- an encounter's `pickup.name` is only acquired after its "
    "enemy is defeated, so it's available starting with the next encounter "
    "and later. For each encounter below, the exact available inventory at "
    "that point is given as a closed set; nothing outside that list is "
    "available yet.\n\n"
    "Read names by meaning, not strict spelling. Examples:\n"
    "- weapon \"Flame Burst Staff\" satisfies weakness \"Flame Burst\" -- the staff produces it. SATISFIES.\n"
    "- pickup \"Voltage Conduit\" satisfies weakness \"Chain Lightning\" -- the conduit channels lightning. SATISFIES.\n"
    "- inventory [\"Iron Greataxe\", \"Obsidian Spike\", \"Storm Essence\"] does NOT satisfy weakness \"Charged Obsidian Spike\" "
    "-- none of those three IS a charged spike, even if combining them might charge one. DOES NOT SATISFY.\n"
    "- pickup \"Healing Potion\" does NOT satisfy weakness \"Holy Light\"."
)


def _inventory_chain(level: dict) -> list[list[str]]:
    """Weapon + pickups from strictly prior encounters, one list per encounter."""
    inventory = [level["player_weapon"]]
    chains = []
    for encounter in level["encounters"]:
        chains.append(list(inventory))
        inventory.append(encounter["pickup"]["name"])
    return chains


def reachability_questions(level: dict) -> dict[str, Noul]:
    return {
        f"encounter_{i}": Noul(
            instructions=f"Does the inventory {inventory!r} satisfy the enemy's weakness {encounter['enemy']['weakness']!r}?",
            criteria={"true": "It satisfies the weakness.", "false": "It does not."},
        )
        for i, (encounter, inventory) in enumerate(zip(level["encounters"], _inventory_chain(level)))
    }


def build_state(case: dict, level: dict) -> dict:
    return {
        "likert_context": LIKERT_CONTEXT,
        "reachability_context": REACHABILITY_CONTEXT,
        "input": case,
        "output": level,
    }
