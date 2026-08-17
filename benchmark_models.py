"""
benchmark_models.py — Compare Llama3 8B, Bonsai 27B, and Gemma2 9B on the
same hardware, same prompts, same conditions.

WHY THIS EXISTS
────────────────
Over the course of building Local AI Workstation, I tried three different
text models on the same RTX 5070 8GB laptop: Llama3 8B (the original),
Bonsai 27B at 1-bit quantization (an experiment in fitting a much bigger
model into the same VRAM budget), and Gemma2 9B (where I landed, after
real usage showed Bonsai rambling badly on simple prompts).

Rather than just describe that swap in prose, this script actually
MEASURES it — same prompts, same machine, one run right after another —
so the README can show real numbers instead of "trust me, it got better."

WHAT IT MEASURES, PER MODEL, PER PROMPT
─────────────────────────────────────────
- Wall-clock response time (seconds) — how long you'd actually wait
- Token count — how many tokens the model produced
- Tokens/sec — Ollama reports this directly (eval_count / eval_duration),
  so we don't have to estimate it ourselves
- Whether the response actually followed length instructions (e.g. did
  "answer in under 10 words" actually get a short answer, or did the
  model ignore that and ramble — this is exactly the failure mode that
  got Bonsai swapped out, so it's worth measuring directly, not just
  trusting a single anecdote)

METHODOLOGY NOTE — read this before treating the numbers as gospel
─────────────────────────────────────────────────────────────────
This is a practical, single-machine comparison for MY specific use case
(a personal AI chat app), not a rigorous, peer-reviewed ML benchmark.
Caveats worth being upfront about:
  - Each prompt runs ONCE per model, not averaged over multiple runs —
    a single run can have noise (background processes, thermal
    throttling, etc). If you want more statistical confidence, bump
    RUNS_PER_PROMPT below and this script will average automatically.
  - "Quality" of the actual answer is judged by a simple word-count
    check, not by a human or another AI grading correctness — this
    measures INSTRUCTION-FOLLOWING (did it obey "keep it short"), not
    factual accuracy.
  - All three models were tested on the same idle machine, but real-world
    performance can vary run to run depending on what else is using the
    GPU at the time.
"""

import requests
import time
import json
import statistics

# ── Config ──────────────────────────────────────────────────────────────
OLLAMA_URL = "http://localhost:11434/api/generate"

MODELS = {
    "Llama3 8B":          "llama3",
    "Bonsai 27B (1-bit)": "MobiusDevelopment/Bonsai-27B-Q1_0-gguf",
    "Gemma2 9B":          "gemma2:9b",
}

# A small, varied prompt set — short factual, instruction-following with a
# strict length limit (this is the exact category that exposed Bonsai's
# rambling), reasoning, and a coding task. Kept short so the benchmark
# doesn't take forever to run across 3 models.
PROMPTS = [
    {
        "label": "short_factual",
        "text": "What is the capital of Japan? Answer in one sentence.",
        "max_expected_words": 15,
    },
    {
        "label": "strict_length_instruction",
        "text": "Tell me a joke in under 10 words.",
        "max_expected_words": 12,  # small buffer since word-counting jokes is fuzzy
    },
    {
        "label": "reasoning",
        "text": "If a train leaves at 3pm going 60mph and needs to travel 180 miles, what time does it arrive? Show your reasoning briefly.",
        "max_expected_words": 80,
    },
    {
        "label": "coding",
        "text": "Write a Python function that returns the factorial of a number. Just the code, no explanation.",
        "max_expected_words": 60,
    },
]

RUNS_PER_PROMPT = 1  # bump this to average multiple runs per prompt/model

# ── Core benchmark logic ──────────────────────────────────────────────────
def run_single_prompt(model_id, prompt_text):
    """
    Sends ONE prompt to ONE model (non-streaming, so we get the full
    response and Ollama's own timing stats in a single response object
    rather than having to sum up streamed chunks ourselves), and returns
    the measurements we care about.
    """
    start = time.time()
    try:
        r = requests.post(
            OLLAMA_URL,
            json={"model": model_id, "prompt": prompt_text, "stream": False},
            timeout=180,  # generous — Bonsai's rambling could genuinely take a while
        )
        wall_clock_seconds = time.time() - start
        data = r.json()

        response_text = data.get("response", "")
        eval_count = data.get("eval_count", 0)
        eval_duration_ns = data.get("eval_duration", 0)

        # Ollama's own reported generation speed — this is the model
        # actually computing tokens, separate from network/queueing time,
        # which is why it can differ slightly from token_count / wall_clock.
        tokens_per_sec = (
            eval_count / (eval_duration_ns / 1_000_000_000)
            if eval_duration_ns > 0 else 0
        )

        return {
            "success": True,
            "response_text": response_text,
            "word_count": len(response_text.split()),
            "token_count": eval_count,
            "wall_clock_seconds": round(wall_clock_seconds, 2),
            "tokens_per_sec": round(tokens_per_sec, 1),
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "wall_clock_seconds": round(time.time() - start, 2),
        }


def run_benchmark():
    """
    Runs every prompt against every model, RUNS_PER_PROMPT times each,
    and returns a nested results dict: results[model_label][prompt_label]
    = list of per-run measurement dicts.
    """
    results = {}

    for model_label, model_id in MODELS.items():
        print(f"\n{'=' * 60}")
        print(f"  Benchmarking: {model_label}  ({model_id})")
        print(f"{'=' * 60}")
        results[model_label] = {}

        for prompt in PROMPTS:
            print(f"  → {prompt['label']}...", end=" ", flush=True)
            runs = []
            for _ in range(RUNS_PER_PROMPT):
                outcome = run_single_prompt(model_id, prompt["text"])
                runs.append(outcome)

            results[model_label][prompt["label"]] = runs

            # Quick console feedback so you can watch it work in real time
            # instead of staring at a blank terminal for several minutes.
            successful = [r for r in runs if r["success"]]
            if successful:
                avg_time = statistics.mean(r["wall_clock_seconds"] for r in successful)
                avg_words = statistics.mean(r["word_count"] for r in successful)
                followed_limit = avg_words <= prompt["max_expected_words"]
                status = "✓ within length" if followed_limit else "⚠ ran long"
                print(f"{avg_time:.1f}s, {avg_words:.0f} words ({status})")
            else:
                print("FAILED — is Ollama running and is this model pulled?")

    return results


# ── Markdown table generation, ready to paste into README.md ────────────
def generate_markdown_table(results):
    lines = []
    lines.append("## Model Benchmark\n")
    lines.append(
        "Tested on the same RTX 5070 8GB laptop, same 4 prompts, one run "
        "each, right after each other. Not a rigorous scientific "
        "benchmark — a practical comparison for this specific app's use "
        "case. See `benchmark_models.py` for exact methodology.\n"
    )
    lines.append("| Model | Avg Response Time | Avg Tokens/sec | Followed Length Instructions? |")
    lines.append("|---|---|---|---|")

    for model_label in MODELS:
        prompt_results = results.get(model_label, {})
        all_runs = [r for runs in prompt_results.values() for r in runs if r["success"]]

        if not all_runs:
            lines.append(f"| {model_label} | — | — | FAILED (see raw JSON) |")
            continue

        avg_time = statistics.mean(r["wall_clock_seconds"] for r in all_runs)
        avg_tps = statistics.mean(r["tokens_per_sec"] for r in all_runs)

        # Specifically check the strict-length-instruction prompt, since
        # that's the exact test case that exposed Bonsai's rambling —
        # worth calling out on its own rather than averaging it away.
        strict_runs = [
            r for r in prompt_results.get("strict_length_instruction", [])
            if r["success"]
        ]
        if strict_runs:
            avg_strict_words = statistics.mean(r["word_count"] for r in strict_runs)
            followed = "✓ Yes" if avg_strict_words <= 12 else f"✗ No ({avg_strict_words:.0f} words avg)"
        else:
            followed = "—"

        lines.append(
            f"| {model_label} | {avg_time:.1f}s | {avg_tps:.1f} tok/s | {followed} |"
        )

    return "\n".join(lines)


if __name__ == "__main__":
    print("Starting benchmark — this will take a few minutes across 3 models × 4 prompts.")
    print("Make sure Ollama is running and all 3 models are already pulled:")
    for label, model_id in MODELS.items():
        print(f"  ollama pull {model_id}")
    print()

    results = run_benchmark()

    # Save raw results — full response text included, so you can also
    # manually spot-check answer QUALITY yourself later, not just speed.
    with open("benchmark_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print("\n✓ Raw results saved to benchmark_results.json")

    markdown = generate_markdown_table(results)
    with open("benchmark_results.md", "w", encoding="utf-8") as f:
        f.write(markdown)
    print("✓ Markdown table saved to benchmark_results.md — paste this into your README")

    print("\n" + markdown)
