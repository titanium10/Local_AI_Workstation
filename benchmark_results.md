## Model Benchmark

Tested on the same RTX 5070 8GB laptop, same 4 prompts, one run each, right after each other. Not a rigorous scientific benchmark — a practical comparison for this specific app's use case. See `benchmark_models.py` for exact methodology.

| Model | Avg Response Time | Avg Tokens/sec | Followed Length Instructions? |
|---|---|---|---|
| Llama3 8B | 6.4s | 19.9 tok/s | ✓ Yes |
| Bonsai 27B (1-bit) | 93.3s | 8.7 tok/s | — |
| Gemma2 9B | 7.8s | 16.9 tok/s | ✓ Yes |