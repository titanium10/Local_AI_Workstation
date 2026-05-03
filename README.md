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




## Log: April 20, 2026 - Infrastructure Evolution: Persistent Memory
Infrastructure Evolution: Persistent Memory (RAG)
Solution Implemented: Integrated AnythingLLM as an orchestration layer to solve the "Stateful Memory" limitation of standard local LLMs.

Vector Database: Deployed LanceDB locally on the 1TB SSD to host persistent "embeddings."

Technical Achievement: Created a Context Injection Pipeline. By embedding an identity.txt file, the model now retains a 100% recall rate for my 269 RIT quantitative profile and long-term academic goals without manual re-entry.

🧪 Multi-Modal Expansion (Vision)
Model Added: Qwen3-Vision-4B-Instruct.

Capability: Enabled visual processing. The system can now analyze screenshots of different environments, providing real-time visual debugging.

VRAM Management: Optimized the RTX 5070’s 8GB VRAM to handle simultaneous text inference and vector search with zero thermal throttling.
### Personal Comments
4/6/26
I'm stil not used to how I have to start a new conversation every time I close the terminal. I will try to code in a something so the ai remembers me and basic information about me everytime I open the termninal and login. Also now it's easier for me to open it rather than typing 
ollama run llama3.1:8B.



###Log: 4/20/26 ###
I know it has been a long time since I did anything but in that time I used the ai a lot, but I noticed a slight problem that struck with me and made it kind of anoyying to use and I would find myself using gemini later. The problem I was facing was the memory... The ai wouldn't remember what I said to it a previous chat and if I shut down the computer or closed the terminal it would forget. So after a bit of resillience I decided to just directly take charge and added AnythingLLM, it also benefited me in many ways even included the Ctrl + SLASH  shortcut which would open a thread for me to ask questions when i'm in the middle of something. And also the Meeting Assistant which i'm really excited to try out later when I have my online classes.



###Log: 5/3/26 Performance Benchmarking & Hardware Telemetry###
I ran a benchmark test mith a weaker model to test my gpu strength for quantization. I have 2 images that I ran a benchmark using the model Phi 3-mini.
-<img width="1920" height="1080" alt="Screenshot 2026-05-03 212205" src="https://github.com/user-attachments/assets/eee3ca16-bbaa-4c13-b32f-afff169a489b" />
-<img width="1492" height="872" alt="Screenshot 2026-05-03 212254" src="https://github.com/user-attachments/assets/00f2f9d3-efe8-45ba-adda-61e5c7336073" />

