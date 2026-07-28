@echo off
:: @echo off means: don't print each command to the screen as it runs.
:: Without this, the window would show every single command before running it.
:: The :: at the start of a line means "comment" — ignored by the computer.

title Samrat's AI Launcher
:: "title" sets the text shown in the top bar of this window.

color 0D
:: "color" sets the terminal colors.
:: First digit = background (0 = black), second digit = text color.
:: D = bright purple/magenta. Matches your app's purple theme!

echo.
echo  ==========================================
echo   Samrat's AI - Starting up...
echo  ==========================================
echo.
:: "echo" prints text to the screen.
:: "echo." prints a blank line.

:: ── STEP 1: Check Ollama is installed ──────────────────────────────
:: "where" checks if a program exists on your computer.
:: If ollama is not found, we warn the user and pause.
where ollama >nul 2>&1
:: >nul sends the normal output to nowhere (we don't want to see it)
:: 2>&1 also sends error output to nowhere
:: We only care about the exit code (0 = found, 1 = not found)
if %errorlevel% neq 0 (
    echo  [ERROR] Ollama not found! Please install it from ollama.com
    pause
    exit
)
echo  [OK] Ollama found

:: ── STEP 2: Start Ollama (if not already running) ──────────────────
:: We check if ollama is already running by asking it for its version.
:: If the request fails, ollama isn't running yet and we start it.
curl -s http://localhost:11434/api/version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [..] Starting Ollama...
    start /min "" ollama serve
    :: "start" runs a program in a new window.
    :: /min means start it minimized so it doesn't clutter your screen.
    :: "" is the window title (empty = default).
    :: "ollama serve" starts the Ollama API server.
    timeout /t 3 /nobreak >nul
    :: "timeout /t 3" waits 3 seconds.
    :: /nobreak means pressing a key won't skip the wait.
    :: >nul hides the countdown message.
    echo  [OK] Ollama started
) else (
    echo  [OK] Ollama already running
)

:: ── STEP 2.5: Pre-load Bonsai 27B into VRAM ────────────────────────
:: Ollama loads a model into VRAM the FIRST time it's asked to generate
:: something — that first load takes several seconds (reading ~3.9GB off
:: disk). Without this step, whoever sends the very first chat message
:: after a fresh restart would eat that delay themselves, on top of
:: normal generation time.
::
:: We avoid that by "warming up" the model right now, before anyone's
:: even opened the app: we send it a throwaway one-word prompt in the
:: background and immediately move on to starting Flask. By the time a
:: real person types a real message, Bonsai is already sitting in VRAM
:: ready to go.
echo  [..] Pre-loading Bonsai 27B into VRAM (warm start)...
start /min "" cmd /c "curl -s http://localhost:11434/api/generate -d "{\"model\": \"MobiusDevelopment/Bonsai-27B-Q1_0-gguf\", \"prompt\": \"hi\", \"stream\": false}" >nul 2>&1"
:: This runs in its own minimized window so it doesn't block the rest of
:: this script — Flask starts loading at the same time the model is
:: warming up, instead of us waiting around for both one after another.

:: ── STEP 3: Start Flask ────────────────────────────────────────────
echo  [..] Starting Flask server...
start /min "" cmd /c "cd /d "C:\Users\samra\OneDrive\Desktop\Local AI" && python app.py"
:: start /min "" — open minimized window with no title
:: cmd /c — open a new command prompt and run the following command
:: cd /d "path" — change to your project folder
::   /d is needed when switching between drives (like C: to D:)
:: && — means "if the previous command succeeded, run this next one"
:: python app.py — starts your Flask server
timeout /t 4 /nobreak >nul
:: Wait 4 seconds for Flask to fully start before continuing
echo  [OK] Flask server started on port 5000

:: ── STEP 4: Start ngrok ────────────────────────────────────────────
echo  [..] Starting ngrok tunnel...
start /min "" ngrok http 5000
:: Starts ngrok in a minimized window, tunneling port 5000
timeout /t 5 /nobreak >nul
:: Wait 5 seconds for ngrok to connect to their servers and get a URL

:: ── STEP 5: Get the ngrok public URL ──────────────────────────────
:: ngrok runs a local API on port 4040 that tells us our current tunnel URL.
:: We use curl to ask it, and PowerShell to extract just the URL from the response.
echo  [..] Getting your shareable ngrok URL...

:: This command asks ngrok's local API what tunnels are open,
:: then uses PowerShell to parse the JSON and pull out the public URL.
for /f "delims=" %%i in ('powershell -Command "(Invoke-WebRequest -Uri http://localhost:4040/api/tunnels -UseBasicParsing).Content | ConvertFrom-Json | Select-Object -ExpandProperty tunnels | Select-Object -First 1 -ExpandProperty public_url"') do set NGROK_URL=%%i
:: for /f — captures the output of a command into a variable
:: "delims=" — don't split the output on any character (keep it all as one line)
:: %%i — the variable that holds each line of output
:: powershell -Command "..." — runs a PowerShell command from inside the batch file
:: Invoke-WebRequest — PowerShell's way of making HTTP requests (like curl)
:: ConvertFrom-Json — converts the JSON response into a PowerShell object
:: Select-Object -ExpandProperty tunnels — gets the "tunnels" array
:: Select-Object -First 1 — takes just the first tunnel
:: -ExpandProperty public_url — gets just the URL string
:: do set NGROK_URL=%%i — saves the result into a variable called NGROK_URL

:: ── STEP 6: Open browser ───────────────────────────────────────────
echo  [..] Opening browser...
start "" "http://localhost:5000"
:: Opens the main app in your default browser.
start "" "http://localhost:5000/stats"
:: Opens the stats dashboard in a second tab automatically.

:: ── STEP 7: Show the summary ───────────────────────────────────────
echo.
echo  ==========================================
echo   Everything is running!
echo  ==========================================
echo.
echo   Local URL:    http://localhost:5000
echo   Shareable:    %NGROK_URL%
echo.
:: %NGROK_URL% prints the variable we captured in step 5
echo   Share the Shareable URL with friends!
echo   It changes every time you restart ngrok.
echo.
echo   Press any key to STOP everything and shut down.
echo  ==========================================
echo.
pause >nul
:: "pause >nul" waits for ANY key press without showing "Press any key..."
:: >nul hides the default pause message so our custom message shows instead.

:: ── STEP 8: Shutdown when user presses a key ───────────────────────
echo.
echo  [..] Shutting down...

:: Kill Flask (python process running app.py)
taskkill /f /im python.exe >nul 2>&1
:: taskkill — Windows command to force-stop a running program
:: /f — force kill (don't ask nicely, just stop it)
:: /im python.exe — kill by image name (the .exe filename)
:: >nul 2>&1 — hide output whether it succeeds or fails

:: Kill ngrok
taskkill /f /im ngrok.exe >nul 2>&1

echo  [OK] All services stopped.
echo.
timeout /t 2 /nobreak >nul
:: Wait 2 seconds so user can read the "stopped" message before window closes
