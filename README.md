# Local_AI_Workstation
#### documenting my journey to become an ai engineer. 

## 🛠 Hardware Configuration
- **Host:** Samsung Book6 Ultra
- **GPU:** NVIDIA GeForce RTX 5070 (8GB VRAM)
- **Architecture:** x86_64 Windows (PowerShell Environment)

## 🧠 Model Specifications
- **Model:** Llama 3.1 8B (Quantized), Llava 7B (Quantized)
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
- **Model:** Llama 3.1 8B, Llava 7B, Bonsai 27B 1-bit
- **Framework:** Ollama (Windows PowerShell)
- **Status:** Successful Local Inference
- **Optimization:** 4-bit quantization utilized for VRAM efficiency.

## 🚀 Technical Highlights & What I Built

As the sole developer of this platform, I focused on making a fast, 100% private AI chat tool that runs entirely on my laptop. Here are the main technical problems I solved:

* **Smart Hardware Management:** I configured the AI model to use 4-bit quantization so it stays under my laptop's 8GB VRAM limit. I also made sure text models (~5.8GB VRAM) and vision models (~7.4GB VRAM) can run without overheating or crashing my computer.
* **Instant Text Streaming:** Instead of making the user wait for the AI to think of the entire answer at once, I used an `XHR onprogress` script. This streams the text word-by-word onto the screen the exact millisecond the local GPU generates it.
* **Remembering User Data:** Standard local AI tools forget everything the moment you close the terminal. I fixed this by connecting a SQLite database and Flask sessions, so the app remembers who you are and keeps your chat history saved safely on disk.
* **Local Document Memory (RAG):** I hooked up ChromaDB as a local memory bank. When I upload a PDF, the app breaks down the text, turns it into vector math, and injects the relevant facts directly into the AI's prompt so it can answer questions about my school studies.



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
I'm stil not used to how I have to start a new conversation every time I close the terminal. I will try to code in a something so the ai remembers me and basic information about me everytime I open the terminal and login. Also now it's easier for me to open it rather than typing 
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
After learning the basics of RAG, I added RAG successfully and tested it out with the ai model, now the gui allso lets users upload documents and images and ask any question about them. added the ai model Llava so I can also analyse images, the model switches between the 2 models every time someone uploads an image. Lasly added a launcher because I have to do more things I launch the website so by adding a .bat file using the help with claude. i can just double click it to launch everything.
### Problem Solved
2 main problems were solved with this code and gui form the feedback I got from testers. Firstly I added RAG so people don't have to copy paste their pdfs and can directly upload them on to the model and ask questions about them seemlessly while getting accurrate data. And the 2nd problem is that people also wanted to test the ai's capability with image analysing. This was a bit challenging to do as I had to add another ai model to the gui but after trial and error and with the help of anthropic's Sonnet 4.6 I succesfully enabled it, Llava is still a really weak model since it's only 7B, but it can still provide somewhat accurate data to the images you ask it to analyse thorough uploading the images from you file explorer or copy-pasting them into the chat.
### Decisions
* The main hardest decision for me was choosing which RAG system to implement my 2 main options were ChromaDB or FAISS. I actually downloaded both of them to check which one's better, I decided to go with ChromaDB since I had previously expiremented with it and is is more begineer friendly as there is no manual index saving like with FAISS.
* So firstly when I decided to add image analyising I wanted the ai to see the image every time the user asked a question about it so i decided to store them as base64 strings in SQLite itslef without affecting my storage. But the problem I noticed with this method was that if I stored them as base64 strings the images would sometimes get corrupted, so instead I decided to store them on my laptop and made a seperate folder(uploads/) which stores only the filename in the database.
* This is a small decision and only completely affecting my storatge, I wanted to decide whether I wanted a RAG system per chat or globally, I first thought globally was better as the ai would know more information as people start uploading more pdfs. But a thought came to me that if I do that and someone puts a file with the same name or same concepts the model can give wrong information to the wrong audience, So i decided to go with per chat RAG systems.
### Personal comments
it's been a long time since I have been active on github, my summatives were going on and I needed to spend more time on them to study, and I also wanted to take a break from ai as I had spent almost everyday adding a new feature. This did take me around 2 hours to implement and I haven't really sent it out for testing yet. going from gemini to Claude has completely changed the quality of the code, but form now I am also thinking to learn more about machine learning python. I haven't really been focusing on my other python repository as am really guilty about it, so I want to learn python so both the repositories stay active. Vibe coded the codebase with AI assistance, but deliberately chose and vetted every architectural decision to handle local hardware constraints.



## Log: 5/30/26 — Live Usage Dashboard & TPS Monitoring
### Overview
I spent some time adding a stats board that displays basic stats like how many messages typed the amount of tokens used and tps. The stats refresh every 3 seconds, it is only accessible by the host, and its not linked anywhere.
### decisions
* I have put the live stats as a dictionary, so it can track if the ai is active or idle, the token count, and the tps. and python is persistent as long as Flask is active, so when someone uses it I can see all of it without affecting the main database.
* I've used the Finally block for making the code cleaner and preventing crashes, by using try/except/finally it always makes the is_generating to false so if the user stops the message, the dashboard won't still show generating and crash.
* I just used Ollama's eval_count and eval_duration which is insanely accurate upto nanoseconds, to give me the most accurate tps.
* the dashboard resets every 3 seconds using the (meta http-equiv="refresh") this is just html so I don't have to update index2.
### Personal comments
this was a short term decision as I spent most of my time looking for internships related to this so I get real feedback from ai engineers and hands on experience, but apart from that the main reason I actually did this is to monitor how the ai model is doing, when many people use it it might slow down so I was thinking to add a queue so others can slowly use it without it crashing or becoming way too slow. This was also a really good excuse for me to learn more about tokens, so it is a win-win situation for me.




## Log: 6/7/26 — Voice to Voice, UI new design, and more settings
### Overview
I added a voice to voice conversation where you can toggle on or off depending upon if you want it or not. Also changed the UI with a maroon red theme and added new animation for aesthetics, also added more settings like toggling light mode/dark mode, toggling on voice response, choosing what voice the ai should respond in, added a toggle for web search, and lastly choosing the temperature of the ai from 0 to 1.
### Problems solved
The main problem I noticed was that you had to type everything to the app and i found that annoying as other models did have voice recognition, and the side setting panel only had one option which made it boring so i added more options, and I also wanted a uncensored version to myself as I also used the ai model for my personal use and I wanted other people using it to feel like it's a normal ai like other models.
### Decisions
* I first decided to use the browsers speach recognition but it required internet and also sends data to google, against my theme of keeping privacy for the users. I decided to Use whisper which runs locally on python and doesn't depend on cloud.
* edge-tts for ai's voice output, it had the best voice quality compared to the other TTS options, it uses Microsoft's servers for audio but conversation isn't sent.
* edge-tts used to read **bold** as 'asterisk asterisk bold asterisk asterisk' so I removed all markdown before sending so the speech sounds good.
* I added a variable called currentaudio so it tracks when the audio is playing and then stops when the user switches conversation or deletes a conversation.
### Personal comments
The main reason I actually added voice to voice was so that I can just speak long messages and its more efficient and the ai responds in a voice so I can hear what it says while doing something else on the computer which is really efficient. I also chose a new UI I like the color maroon red, and purple really didn't seem my fit and I heavily like aesthetics so I also added more animation while I'm at changing the UI. I also added a uncensored version for myself because I use it for my personal purposes, and I still made a censored version for other IP's that are not the local host. Overall I think this went great I spent around 1.5 hours setting this up, with the help of Claude for coding. Prompting this and testing the results out is really fun and with all of this I am also learning new things because I tell Claude to explain me everything it changes.




## Log: 6/22/26 — adding new quality of life features to help the user and make it more like other ai ui.
### Overview
I added 20 quality of life features to the chat and the website ui. These features were: Code copy button, Chat search, ... menu on the chat where you can rename. pin. export. and .delete, Timestamps, chat exporting, character counter, a new developed welcome screen with 6 prompts, scroll to bottom button, edit last message button, ai chat naming, persona, typing indicator, message counter, image fullscreen, stop generating button, retry message button, token counter, new keyboard shortcuts, sound effect when the ai is done generating, ai's active status on the app ui.
### Problem Solved
* there wasn't a way to find all chats without scrolling through the entire thing so I added a chat search bar.
* App,py had one main system prompt which would not have been accurate for many different problems, so added a persona field in the settings so users can add a main system prompt.
* code and messages couldnt be copied without highlighting the entire passage so added a copy text button.
* I couldnt know when ollama was active without checking the app.py stats page, so I moved a small green and red light indicator to show when ollama is active.
* the chat sidebar only showed the name of the conversation and a delete button, so I added new features like message count, and message pin.
* when you opened a new conversation there was a blank page with a text box, so I added a welcome screen with a few prompts to make the conversation look active.
* There wasn't a way to mess with chats apart from deleting them, so I added pining, renaming, exporting, and deleting.
* There wasn't a way to tell how many tokens the entire conversation was and when it was coming to an end because the model has a small token context, so I added a estimated token counter at the top right so see how long the chat is.
* There wasn't any timestamps on messages, so I added a timestamp under every message.
### Decisions
* The ai title selection is made right after the first response so it doesn't affect the performance and gives better titles with barely and speed cost.
* Persona is capped at 1000 characters to prevent bloating and misbehaving.
* the token counter uses a equation of 1 token = 4 characters, which gives an estimate of how many tokens are there in a chat.
* sound affect is from web audio API, to generate a ping after generation.
### Personal comments
It has been a long time since I made any changes to the app but I have used it a lot, I had come to india for vacation and couldnt find time, and I am planning to buy a seperate gpu with more vram so I can add more features and a better model and try out fine tuning. Overall this project today was easy I did require manually checking all the problems from testers and spent a hour testing if those problems were true and finding other problems I wanted to solve by comparing them to another ai UI like Claude and Gemini. Doing this was really fun because I did try to find loopholes and try to jailbreak the ai for a few minutes, and I will be fixing those in the future projects. 




## Log: 7/2/26 — Add concurrency queue: FIFO(First-In First-Out) ticket system with lock-based GPU access control, live queue position shown in UI
### Overview
Added a FIFO (First-In First-Out) request to save ollama from continuous generation requests. Since the Vram would be a constraint top run more than one generation than a time. Multiple people using ngrok didn't have protection to go against it. This fixes the queuing system, with the live queue-position in the UI.
### Problems Solved
* There wasn't any protection, so if multiple people sent messages at the same time, it would cause GPU contention, or a request getting starved.
* Users didn't have any feedback while waiting as there was only a thinking animation, without any indication of anything happening.
* To guarantee fairness added a first-come first-serve system without adding any complicated infrastructure.
### Decisions
* Used Python's built in threading.lock() as the gatekeeper, this solves any complex coding, and can hold only one thread at a time, which will guarantee that Ollama never gets 2 generation calls at once.
* used a pooling loop that checks every 0.3 to 0.5 seconds, and instead of a elegant event based wake-up system there will the a simpler reason about and harder to get subtly wrong at this scale with multiple concurrent users not thousands.
* Also put the waiting logic inside the streaming generator function, instead of being before the HTTP response. It will show live that "You are #2 in queue" and it updates through the SEE/XHR stream, instead of the browser being with no response.
* It is wrapped around a lock-release logic in a finally block so it will always run. Whether it's success, error, or user hitting stop. Since the lock never gets released it would not freeze for all the other users.
* Added a 300-second timeout as a safety net just in case ollama gets bugged and stuck so people don't wait forever.
### Personal comments
After spending time on the web app I have been creating I have moved on to this project again, to take a break while still learning. I added this feature to prevent people from having a tough user experience when multiple people are using the app. I noticed this when me and my dad were using generating responses at the same time, and the ai sometimes didn't respond or didn't read the response, which would have been more common if there were more users, so I fixed the whole app so now there is a queue with a really small waiting time.




## Log 7/7/26 - Real tokenizer
### Overview
Replaced the initial token counter (1 token = 4 characters) with the llama 3 tokenizer, and it provides accurate token data rather than a estimate. also added a /api/tokenize and also updated the frontend counter to update it.
### Problems Solved
* Based on the text type and the length of the conversation the estimate can be up to 30% off by the actual token count, which will matter when you are coming close to the 8k context limit of llama 3.1.
* Meta's official Llama3.1 tokenizer on Hugging Face uses a gated access, and I worked around this by using the public open mirror (NousResearch/Meta-Llama-3-8B) that gives the same identical tokenizer.
### Decisions
* Used hugging face's tokenizer library instead of OpenAi's tiktoken tokenzier, because in a way tiktoken doesn't match the vocabulary of llama 3.1 so the tokens will still be inaccurate.
* Tokenizer loads right after flask loads, and then gets cached to the disk immediately by the library after the first successful run, then there are no needed network calls for the future.
* Wrapped in a tokenizer load in try/except with a fallback to the old estimate because if it fails the app will still be working a bit inaccurately based on the estimates.
* On the front it will show the character estimate instantly with no lag, and when the exact count responds in the backend it avoids the counter being frozen while waiting for the network round-trip.
* Also added a request-ID quard so that a slow tokenizer response from the chat the user already navigated away from, it won't be able to overwrite the counter for another chat they are viewing.
### Personal Comments
Because of the small context window of the chat, it is easy to reach the context limit fast, and to block that and know when the chat is coming to the end I added a tokenizer but the problem with the tokenizer was that it was inaccurate, and sometimes the tokenizer would show 5k tokens and the chat would actually be at 8k and start hallucinating, which was a big problem, so for that reason I added a actual Llama tokenizer where it can give the most accurate number of tokens so you know when the chat is coming to an end.




## Log 7/28/26 - Model Upgrade and Semantic Context Compression
### Overview
Swapped Llama# 8B to Bonsai 27B, with 1-bit quantization that comfortably fits in the same vram while being better at reasoning and complex tasks. With that also replaced the old sliding-window context which was 6 messaged with a semantic context compression. so older messages keep running as a summary instead of being forgotten. Added a start bat file so the new model is pre-loaded into the VRAM before the first message is sent.
### Problem Solved
* Llama3 8B was the absolute best model that could fit in 8GB VRAM, but with Bonsai 27B using 1bit quantization(3.9gb) you can break that ceiling with every single reasoning and tasks, while using less vram and without more vram.
* When conversations became longer they lost memory after about 6 messages, then after that the model would purely guess what the previous messages were about, and would not know about what the previous messages were about.
* First message after every restart would have a multi-second wait while Ollama loaded the model into the VRAM.
### Decisions
* Kept Llava as the dedicated model for messages with images rather than switching to Bonsai. Bonsai does come with a vision component but the community packaged Ollama version doesn't directly state that it's included. So it was better to keep a working image understanding rather than a broken one.
* Compression triggers once a chat passes 8 raw messages, summarizing the oldest 4 messages, it keeps the raw message count without needing a hard cutoff.
* The summarization call uses Bonsai rather than another dedicated model, trading a small extra latency for one less moving part in the system.
* the warm-start runs on its own in background window so it doesn't block Flask or Ngrok.
### Personal comments
This whole month I have been working on another project, and I decided to make a small but drastic change because of a few complaints regarding the memory issue, this took me around an hour to implement, and it works great as there is a new smarter model and a better memory system. I am also using this system in a small raspberry pi system I did and it works really well, over time I might decide to test this in multiple different devices and run the a similar program on it so that it always stays on.





## Log 8/17/26 - Model Benchmark and Swap: Llama3 8B vs Bonsai 27B vs Gemma2 9B
### Overview
A few weeks back I swapped the text model Llama3 8B to Bonsai 27B (1-bit quantization), I was looking forward to more parameters and a smarter model in the same VRAM allocation. But real usage faced a problem, basic simple prompts were coming really bloated and slow. So I swapped the model to Gemma2 9B to fix it, then built benchmark_models.py to measure all 3 models instead of relying on a anecdote. so the final call was based on real numbers, and not just a call.
### Problem Solved
* Bonsai 27B's 1-bit quantization caused a massive quality degrade. a short prompt like "tell me a joke in under 10 words" produced 1,192 tokens and took over 5 minutes instead of a short answer.
* There was no way to compare the models objectively. And decisions were based on self testing, and the data wasn't consistent or repeatable.
* Needed Proof for why I changed the model from Bonsai to Gemma, so needed a rigorous test to show why Bonsai got replaced.
### Decisions
* Built the Benchmark with 4 prompts (short factual, strict length instructions, reasoning, coding) rather than a single strict length instructed prompt that targets the same failure mode that got Bonsai replaced.
* Measured tps directly from Ollama's eval_count/eval_duration fields rather than giving a good estimate. So the numbers show the actual generation speed.
* Kept the benchmark honest about its own limits: gave 1 run per prompt, a single machine, and a word-count-based instruction that follows check rather than a human or a AI-graded quality documented directly in the script.
180-second timeout per prompt, it is generous for models that take time for a response. But Bonsai failed to finish in the the time given with the prompt within that window. So the timeout became a data point to consider.
### Personal comments
Its been over 2 weeks since I did any changes or commits to this repo, I have been really busy as school started and I travelled. But during that time I tried out multiple linux systems on a raspberry pi to have future projects related to it. So I have been getting a few comments and feedback about the new model change, and people were annoyed about the really long wait time for simple tasks and prompts, and that made them refuse to take it. I thought it was a problem with the code so I tried to run a few checks and tweak the code a few times, and then when i finally ran the Bonsai 27B on Ollama I realized it was the model itself that was the problem. After that I ran a few benchmarks again because I did get new models and I was deciding what to put as a new text model so I put 3 models side by side and got the best performing model which was the Gemma2 9B by google. till now I thought having more parameters means the model would be better but I came to the conclusion after studying about it that there are lots of other factors like hallucination, call speed and many more that affect a model's performance.





## Log 8/22/26 - Environment-based configuration
### Overview
Moved every hardcoded value out of app.py. The windows-only ChromaDB path, Flask secret key, active model names, and port number to a .env file loaded with python-dotenv. Also added .env.example as a safe template for anybody trying to clone the repo, so they know what to configure without looking at my values.
### Problems Solved
* CHROMA_PATH was hardcoded as a Windows path. Which only worked in the laptop I am using, moving to another computer or sharing the repo would have broken it.
* The Flask SECRET_KEY, which signs the session cookies, it was only in plain text directly in the public Github repo. the real security problem hadn't been caught till the reviewing of the codebase for improvements.
* There wasn't a good way to test other models or ports without editing code.
### Decisions
* Used os.getenv("KEY", fallback) everywhere instead of using os.environ["KEY"], a missing .env value brings it to a safe default (or, for CHROMA_PATH specifically, a empty string that is failing rather than a quiet working on my machine and breaking elsewhere)
* .env is gitignored and it's never in Github; .env.example, is in instead it has the placeholder names, key names, so the repo is cloneable without revealing my secret keys.
* Chose not to hardcore a "real looking" fallback for SECRET_KEY, the fallback is obvious on purpose ("change-me-in-your-env-file") so nobody ships it to production accidently without using it.
### Personal comments
The reason I added this feature was that there were a few of my friends that wanted to clone my repo or copy the same thing on their pcs. and I had a few things that couldn't be cloned on their pcs, so I decided to add a .env so that they can add their own keys and other private details. I will also be adding more features related to this in the future as more people start using this.
