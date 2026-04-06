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
### Personal Comments
It was kind of confusing running a ai model locally for the first time without any information, I did not watch any tutorials for learning what to do, and had to figure it out by myself I did use gemini later on to download the model and run it. It is confusing since is also doesn't have memory it is kind of annoying too. I will try to find a way to make it always recognise who i am the second I launch it.




## Log: April 6, 2026 - Workflow Optimization & Utility Validation

### 🛠️ Infrastructure Update: Low-Latency Access
* **Feature:** Implemented a Global Hotkey Trigger for Local Inference.
* **Technical Detail:** Configured a PowerShell-based execution script mapped to `Ctrl + Alt + L`. 
* **Objective:** Reduced "Time-to-Inference" by bypassing manual terminal navigation. This establishes a seamless "Co-Pilot" environment for real-time development and academic research.

### 🧪 Capability Testing: Academic Integration (Science)
* **Task:** Utilized the Llama 3.1 8B model to assist with complex Science curriculum analysis.
* **Result:** Successfully leveraged the model’s parametric knowledge to clarify advanced scientific concepts and structure homework responses. 
* **Validation:** Confirmed the model's utility as a high-fidelity academic tutor, proving that local LLMs are viable tools for GPA optimization and competitive exam preparation.
### Personal Comments
I'm stil not used to how I have to start a new conversation every time I close the terminal. I will try to code in a something so the ai remembers me and basic information about me everytime I open the termninal and login. Also now it's easier for me to open it rather than typing 
ollama run llama3.1:8B
