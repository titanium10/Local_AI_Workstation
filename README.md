# Local_AI_Workstation
documenting Running Llama 3.1 8B in my laptop

## 🛠 Hardware Configuration
- **Host:** Samsung Book6 Ultra
- **GPU:** NVIDIA GeForce RTX 5070 (8GB VRAM)
- **Architecture:** x86_64 Windows (PowerShell Environment)

## 🧠 Model Specifications
- **Model:** Llama 3.1 8B (Quantized)
- **Parameters:** 8 Billion
- **Quantization:** 4-bit (Optimized for 8GB VRAM)
- **Runtime:** Ollama (Local Inference Engine)

## 📊 Performance Benchmarks
| Metric | Result |
| :--- | :--- |
| **VRAM Utilization** | ~5.8GB / 8.0GB |
| **Inference Speed** | ~110+ Tokens/Sec |
| **Privacy Status** | 100% Offline |

## 🚀 Deployment Process
1. **Infrastructure:** Initialized Ollama server via PowerShell.
2. **Model Pull:** Leveraged `ollama pull llama3.1:8b` to sync weights locally.
3. **Validation:** Verified GPU offloading using `ollama ps`.

## 📂 Code Integration (Work in Progress)
Plan to integrate this local model into my `My-Python-Journey` project using the Ollama Python library for automated study-aid generation.






**Date:** April 5, 2026
**Hardware:** RTX 5070 (8GB VRAM) | Samsung Book6 Ultra

### Technical Milestone
- **Model:** Llama 3.1 8B
- **Framework:** Ollama (Windows PowerShell)
- **Status:** Successful Local Inference
- **Optimization:** 4-bit quantization utilized for VRAM efficiency.

### Achievement
Successfully bypassed cloud-based AI to run a private, 8-billion parameter model on local silicon. This setup provides 100% data privacy and zero latency for my 9th-grade developer workflow.
