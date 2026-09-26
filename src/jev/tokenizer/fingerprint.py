"""Fingerprint jev's tokenizer by seeded differential fuzzing against local candidates."""

import os
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"

import hashlib
import json
import logging
import random
import statistics
import string
import unicodedata
from pathlib import Path

import tiktoken
from dotenv import load_dotenv
from transformers import AutoTokenizer
from typesafe_sdk import Noul, TypeSafeClient

logging.getLogger("huggingface_hub").setLevel(logging.ERROR)

SEED = 0
N = 200
TRIES = 20000
BINS = (8, 32, 96)
CAP = 3
K = 3
CACHE = Path("traces/tokenizer/jev.json")
RNG = random.Random(SEED)

TOKENIZERS = {
    "tt": {
        "cl100k": "cl100k_base",
        "o200k": "o200k_base"
    },
    "hf": {
        "Qwen3": "Qwen/Qwen3-8B",
        "Llama3": "NousResearch/Meta-Llama-3.1-8B",
        "Llama2": "NousResearch/Llama-2-7b-hf",
        "Mistral": "mistralai/Mistral-7B-v0.1",
        "Gemma2": "unsloth/gemma-2-9b",
        "DeepSeek": "deepseek-ai/DeepSeek-V3",

        "BERT": "bert-base-cased",
        "RoBERTa": "roberta-base",
        "DeBERTa3": "microsoft/deberta-v3-base",
        "XLM-R": "FacebookAI/xlm-roberta-base",
        "ModernBERT": "answerdotai/ModernBERT-base",
    },
    "custom": {
        "o200k-qwenpre": ("o200k_base", r"(?i:'s|'t|'re|'ve|'m|'ll|'d)|[^\r\n\p{L}\p{N}]?\p{L}+|\p{N}| ?[^\s\p{L}\p{N}]+[\r\n]*|\s*[\r\n]+|\s+(?!\S)|\s+"),  # o200k merges behind Qwen's pretokenizer regex
    }
}

def load_tokenizers():
    tokenizers = {}
    for name, enc in TOKENIZERS["tt"].items():
        e = tiktoken.get_encoding(enc)
        tokenizers[name] = lambda s, e=e: len(e.encode(s, disallowed_special=()))
    for name, repo in TOKENIZERS["hf"].items():
        try:
            tok = AutoTokenizer.from_pretrained(repo)
        except Exception as err:
            print(f"skip {name}: {str(err).splitlines()[0][:100]}")
            continue
        tokenizers[name] = lambda s, tok=tok: len(tok.encode(s, add_special_tokens=False))
    for name, (base, pat) in TOKENIZERS["custom"].items():
        o = tiktoken.get_encoding(base)
        e = tiktoken.Encoding(name=name, pat_str=pat, mergeable_ranks=o._mergeable_ranks, special_tokens=o._special_tokens)
        tokenizers[name] = lambda s, e=e: len(e.encode(s, disallowed_special=()))
    return tokenizers

def gen_sample():
    n = RNG.choice((4, 16, 64, 128))
    kind = RNG.randint(0, 6)
    if kind == 0:
        return "".join(RNG.choice(string.digits) for _ in range(n)), "digits"
    if kind == 1:
        return "a" + RNG.choice(" \t\n") * n + "b", "space"
    if kind == 2:
        return "".join(RNG.choice(string.ascii_letters + string.punctuation) for _ in range(n)), "ascii"
    if kind == 3:
        return "".join(chr(RNG.randint(0x4E00, 0x9FFF)) for _ in range(n)), "cjk"
    if kind == 6:
        return " ".join("".join(RNG.choice(string.ascii_lowercase) for _ in range(RNG.randint(2, 6))) + "'" + RNG.choice(("s", "t", "re", "ve", "m", "ll", "d")) for _ in range(n)), "contract"
    lo, hi, cat = (0x1F300, 0x1FAFF, "So") if kind == 4 else (0x80, 0x2FFFF, "L")
    s = ""
    while len(s) < n:
        c = chr(RNG.randint(lo, hi))
        if unicodedata.category(c).startswith(cat):
            s += c
    return s, "emoji" if kind == 4 else "other"

def jev_count(client, text):
    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    h = hashlib.sha1(text.encode()).hexdigest()[:16]
    if h not in cache:
        v = [client.system_one(state=text, questions={"q": Noul(instructions="Is this about billing?")}, model="jev-latest").usage.input_tokens for _ in range(K)]
        cache[h] = v[0] if len(set(v)) == 1 else None
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        CACHE.write_text(json.dumps(cache))
    return cache[h]

def main():
    # setup
    load_dotenv()
    tokenizers = load_tokenizers()
    names = list(tokenizers)
    pairs = [(i, j) for i in range(len(names)) for j in range(i + 1, len(names))]
    best = [[0] * (len(BINS) + 1) for _ in pairs]
    bestr = [dict() for _ in pairs]
    samples = [("", -1)]
    ccov, csum = 0, 0

    # generate sample
    for _ in range(TRIES):
        if len(samples) >= N:
            break
        s, r = gen_sample()
        col = [tokenizers[name](s) for name in names]
        g = [abs(col[i] - col[j]) for i, j in pairs]
        b = sum(len(s) > t for t in BINS)
        cov = ccov + sum(min(g[k], CAP) - min(bestr[k].get(r, 0), CAP) for k in range(len(pairs)) if g[k] > bestr[k].get(r, 0))
        sm = csum + sum(g[k] - best[k][b] for k in range(len(pairs)) if g[k] > best[k][b])
        if (cov, sm) > (ccov, csum):
            for k in range(len(pairs)):
                if g[k] > best[k][b]:
                    best[k][b] = g[k]
                if g[k] > bestr[k].get(r, 0):
                    bestr[k][r] = g[k]
            samples.append((s, r))
            ccov, csum = cov, sm

    # print sample
    robust = [row[-1] for row in best]
    grid = {(i, j): robust[k] for k, (i, j) in enumerate(pairs)}
    print(f"seed {SEED}  samples {len(samples)}  pairs {len(pairs)}  coverage {ccov}\n")
    print(f"{'':15}" + "".join(f"{j:>5}" for j in range(len(names))))
    for i, a in enumerate(names):
        print(f"{i:>2} {a:<12}" + "".join(f"{('-' if i == j else grid[(min(i, j), max(i, j))]):>5}" for j in range(len(names))))

    # measure jev
    P, Q = "a\n", "\nz"
    with TypeSafeClient() as client:
        base = jev_count(client, P + Q)
        raw = {s: jev_count(client, P + s + Q) for s, r in samples[1:]}
    reg = {s: r for s, r in samples[1:]}
    J = {s: v - base for s, v in raw.items() if v is not None}
    cPQ = {n: tokenizers[n](P + Q) for n in names}

    # score each candidate
    used = sorted({reg[s] for s in J})
    probes = {r: [s for s in J if reg[s] == r] for r in used}
    C = {n: {s: tokenizers[n](P + s + Q) - cPQ[n] for s in J} for n in names}
    rate = {n: {r: sum(C[n][s] == J[s] for s in probes[r]) / len(probes[r]) for r in used} for n in names}
    order = sorted(names, key=lambda n: -sum(C[n][s] == J[s] for s in J))
    print(f"\nmatch rate by kind\n{'':13}" + "".join(f"{r}({len(probes[r])})".rjust(13) for r in used))
    for n in order:
        print(f"{n:<13}" + "".join(f"{rate[n][r]:>13.2f}" for r in used))
