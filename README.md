# Local_AI_Workstation
documenting my journey thorough my dream to become an ai engineer. (all the coding has been done with ai, firstly I used gemini then moved to claude Sonnet 4.6 and Opus 4.6/Opus 4.7, I only prompt the ai to do and if I notice a problem I ask it to rewrite and change that part of the code)

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



### Log: 4/20/26 
I know it has been a long time since I did anything but in that time I used the ai a lot, but I noticed a slight problem that struck with me and made it kind of anoyying to use and I would find myself using gemini later. The problem I was facing was the memory... The ai wouldn't remember what I said to it a previous chat and if I shut down the computer or closed the terminal it would forget. So after a bit of resillience I decided to just directly take charge and added AnythingLLM, it also benefited me in many ways even included the Ctrl + SLASH  shortcut which would open a thread for me to ask questions when i'm in the middle of something. And also the Meeting Assistant which i'm really excited to try out later when I have my online classes.



### Log: 5/3/26 Performance Benchmarking & Hardware Telemetry
I ran a benchmark test mith a weaker model to test my gpu strength for quantization. I have 2 images that I ran a benchmark using the model Phi 3-mini.
- <img width="1200" height="600" alt="Screenshot 2026-05-03 212205" src="https://github.com/user-attachments/assets/eee3ca16-bbaa-4c13-b32f-afff169a489b" />
- <img width="1200" height="600" alt="Screenshot 2026-05-03 212254" src="https://github.com/user-attachments/assets/00f2f9d3-efe8-45ba-adda-61e5c7336073" />
-  "Observed significant VRAM delta between text-only and vision models. Qwen3-Vision-4B requires ~7.4GB VRAM (92% utilization) compared to Llama 3.1 8B's ~5.8GB, despite having fewer parameters. Thermal performance remains stable at 41°C due to low active power draw (23W)."



## Log:5/4/26 Setting up a local Vector Memory
### Overview
Successfully integrated ChromaDB as a persistent vector database layer. This allows the local workstation to store and retrieve information based on semantic meaning (intent) rather than just keyword matching. This is the foundation for my future RAG (Retrieval-Augmented Generation) system to assist with IB Math studies.

#### Key Features Implemented
Persistent Storage: Transitioned from EphemeralClient to PersistentClient to ensure data survives system reboots.

#### Collection Management: 
Used get_or_create_collection to allow for seamless data updates without duplicating database entries.

#### Semantic Search: 
Verified that the system can find related concepts (e.g., matching "portable computer" to "laptop") using vector embeddings.

### Personal Comments
Yes, I did use ai for the code and integration, this is my first time getting involved in storing data as a vector database. I'm actually really flabbergasted on how ai has now improved and I ran this on my computer with the help of gemini. I am a solo man who wants to learn all of this AI myself using ai's help. This is getting more interessting and yes I was commited so I also did a project today.



## Log 2: 5/4/26 Local_Inference_Deployment (app.py)
### Overview
I made a significant progress from locally hosting to web-based interface using streamlit to host app.py. I also integrated Ngrok so I can give this ai feature to other people around me that aren't connected to my wifi and also made it secure via https link. I aLso learnyt how to manage multiple powershell windows simuntaniously running different things.
### personal comments
Today was a great day, I set up 2 really important things in a day with the amount of time I had. Since today was a holiday it gave me extra time work on ai. Im kind of happy with what I have now, the ai model has some issues like the context window is only one question and it can't see previous questions. I will update that in the future, and make it more better so other people can use it reliably. I have given this link out and will ask for feedback from other users so I can improve my model and I will try to look into fine tuning in the future.



## Log: 5/10/26 — Full Stack Rebuild: Flask + SQLite Migration
### Overview
Completely rebuilt the web interface from Streamlit to a custom Flask application with a hand-coded HTML/CSS/JS frontend. This was a major architectural upgrade driven by Streamlit's fundamental limitations around multi-user session persistence. it is way more functional with more graphical representations.
### Problem Solved
Streamlit resets `session_state` on every page reload — meaning users lost their entire chat history the moment they refreshed. No workaround existed without a proper backend.
### Features Added
- ✅ Persistent chat history per user (survives reload, close, reopen)
- ✅ Multi-chat with sidebar navigation
- ✅ Real-time token streaming (word by word like ChatGPT)
- ✅ Stop generation mid-response
- ✅ Dark/light mode toggle (saved to localStorage)
- ✅ Emoji picker with 28 emojis
- ✅ ngrok tunnel for external access
### Personal Comments
Iv've been working on this basically the whole week after setting up streamlit and ngrok. I moved to flask it was a bit harder to set up but it was way more convenient since now people can have private chats without other people looking at it or having the doubt that I will look at it. This took way to long than what I thought it would andf streamlit would not do what I want so that also wasted time but in all I think I have learnt a lot about this and still want to learn more. I also made the phone web page for it so people using phone can also access it.




## Log: 5/27/26 - RAG System, Image analyser, and .bat launcher.
### Overview 
After learning the basics of RAG, I added RAG succesfully and tested it out with the ai model, now the gui allso lets users upload documents and images and ask any question about them. added the ai model Llava so I can also analyse images, the model switches between the 2 models every time someone uploads an image. Lasly added a launcher because I have to do more things I launch the website so by adding a .bat file using the help with claude. i can just double click it to launch everything.
### Problem Solved
2 main problems were solved with this code and gui form the feedback I got from testers. Firstly I added RAG so people don't have to copy paste their pdfs and can directly upload them on to the model and ask questions about them seemlessly while getting accurrate data. And the 2nd problem is that people also wanted to test the ai's capability with image analysing. This was a bit challenging to do as I had to add another ai model to the gui but after trial and error and with the help of anthropic's Sonnet 4.6 I succesfully enabled it, Llava is still a really weak model since it's only 7B, but it can still provide somewhat accurate data to the images you ask it to analyse thorough uploading the images from you file explorer or copy-pasting them into the chat.
### Decisions
* The main hardest decision for me was choosing which RAG system to implement my 2 main options were ChromaDB or FAISS. I actually downloaded both of them to check which one's better, I decided to go with ChromaDB since I had previously expiremented with it and is is more begineer friendly as there is no manual index saving like with FAISS.
* So firstly when I decided to add image analyising I wanted the ai to see the image every time the user asked a question about it so i decided to store them as base64 strings in SQLite itslef without affecting my storage. But the problem I noticed with this method was that if I stored them as base64 strings the images would sometimes get corrupted, so instead I decided to store them on my laptop and made a seperate folder(uploads/) which stores only the filename in the database.
* This is a small decision and only completely affecting my storatge, I wanted to decide whether I wanted a RAG system per chat or globally, I first thought globally was better as the ai would know more information as people start uploading more pdfs. But a thought came to me that if I do that and someone puts a file with the same name or same concepts the model can give wrong information to the wrong audience, So i decided to go with per chat RAG systems.
### Personal comments
it's been a long time since I have been active on github, my summatives were going on and I needed to spend more time on them to study, and I also wanted to take a break from ai as I had spent almost everyday adding a new feature. This did take me around 2 hours to implement and I haven't really sent it out for testing yet. going from gemini to Claude has completely changed the quality of the code, but form now I am also thinking to learn more about machine learning python. I haven't really been focusing on my other python repository as am really guilty about it, so I want to learn python so both the repositories stay active. The coding is completely done with ai and I only prompt made it.
