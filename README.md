# ZED Mitra — Chatbot for ZED Certification Scheme
### Ministry of MSME · Government of India

This is a simple chatbot that answers questions about the ZED scheme.
Built with: Python (FastAPI backend) + HTML (frontend) + Groq AI (free LLM API)

No prior coding knowledge needed to run this. Follow every step exactly.

---

## What this project does

- Officer or MSME owner opens a webpage
- They type a question like "how do I get Bronze certification?"
- The chatbot answers using official ZED knowledge
- Works in 12 Indian languages
- Your Groq API key stays on the server — never visible to users

---

## Folder structure (what each file does)

```
zed_chatbot/
│
├── backend/
│   ├── main.py             ← The brain. Handles questions, calls Groq AI
│   ├── requirements.txt    ← List of Python packages needed
│   └── .env.example        ← Template for your secret API key file
│
├── frontend/
│   └── index.html          ← The chatbot webpage (what users see)
│
├── docs/
│   └── question_bank.json  ← 50 test questions to try before demo
│
└── README.md               ← This file
```

---

## STEP 1 — Install Python

Skip this if you already have Python.

1. Go to https://python.org/downloads
2. Download Python 3.11 or newer
3. During install — CHECK the box that says "Add Python to PATH"
4. Open Command Prompt (Windows) or Terminal (Mac/Linux)
5. Type this and press Enter:
   ```
   python --version
   ```
   You should see something like: Python 3.11.4

---

## STEP 2 — Get your free Groq API key

Groq gives you a free API key. No credit card needed.

1. Go to https://console.groq.com
2. Sign up (use any email — Google login works)
3. After login, click "API Keys" on the left sidebar
4. Click "Create API Key"
5. Give it a name like "zed-poc"
6. COPY the key — it looks like: gsk_xxxxxxxxxxxxxxxxxxxx
7. Save it somewhere safe (Notepad is fine for now)

---

## STEP 3 — Set up the project

Open Terminal (Mac/Linux) or Command Prompt (Windows).

### 3a. Go into the backend folder
```bash
cd zed_chatbot/backend
```

### 3b. Create a virtual environment
This keeps your project's packages separate from everything else on your computer.
```bash
python -m venv venv
```

### 3c. Activate the virtual environment

On Windows:
```bash
venv\Scripts\activate
```

On Mac or Linux:
```bash
source venv/bin/activate
```

You'll see (venv) appear at the start of your terminal line. That means it worked.

### 3d. Install required packages
```bash
pip install -r requirements.txt
```
This downloads 5 small packages. Takes 1-2 minutes.

---

## STEP 4 — Add your API key

### 4a. Create the .env file
In the backend folder, create a new file called exactly: `.env`
(note the dot at the start — it's important)

On Windows (in Command Prompt):
```bash
copy .env.example .env
```

On Mac/Linux:
```bash
cp .env.example .env
```

### 4b. Edit the .env file
Open `.env` in any text editor (Notepad works).
Replace `your_groq_key_here` with your actual Groq key:

```
GROQ_API_KEY=gsk_your_actual_key_here
APP_ENV=development
PORT=8000
```

Save and close.

IMPORTANT: Never share this .env file with anyone. Never put it on GitHub.

---

## STEP 5 — Run the chatbot locally

Make sure you're still in the backend folder with (venv) active, then:

```bash
uvicorn main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

Now open your browser and go to: http://localhost:8000

The chatbot should load. Try asking: "How do I apply for Bronze certification?"

---

## STEP 6 — Test before demo

Use the questions in docs/question_bank.json to test.

Quick test list (try these one by one):
1. What is ZED certification?
2. How do I apply for Bronze?
3. What documents do I need?
4. I am a micro enterprise — how much subsidy will I get?
5. I have ISO 9001 — does it help in ZED?
6. What is the ZED Pledge?
7. How long does Bronze certification take?
8. I am from Assam — do I get extra benefits?

Also test the language dropdown — select Hindi and ask the same question.

---

## STEP 7 — Deploy to Render (free hosting, public URL)

This makes the chatbot available on the internet so officers can access it.

### 7a. Put your code on GitHub

1. Go to https://github.com and create a free account
2. Create a new repository called "zed-mitra"
3. Make it PUBLIC
4. Upload all your files EXCEPT the .env file
   (the .gitignore file already prevents .env from being uploaded)

### 7b. Deploy on Render

1. Go to https://render.com and sign up (free, use GitHub login)
2. Click "New +" → "Web Service"
3. Connect your GitHub account
4. Select your "zed-mitra" repository
5. Fill in these settings:
   - Name: zed-mitra
   - Region: Singapore (closest to India)
   - Branch: main
   - Root Directory: backend
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Click "Advanced" → "Add Environment Variable"
   - Key: GROQ_API_KEY
   - Value: paste your Groq key here
7. Click "Create Web Service"

Render will take 3-5 minutes to build and deploy.

You'll get a URL like: https://zed-mitra.onrender.com

That's your public chatbot URL. Share this with officers for the POC demo.

### 7c. Update API_BASE in frontend

Open frontend/index.html
Find this line (around line 180):
```javascript
const API_BASE = window.location.hostname === 'localhost'
  ? 'http://localhost:8000'
  : window.location.origin;
```

This is already set up correctly. When served from Render, it auto-detects the URL.

---

## STEP 8 — Upgrade to Ministry API key later

When the Ministry provides an official API key (or you want to use a different LLM):

1. Open backend/.env (or Render environment variables)
2. Replace the Groq key with the new key
3. In backend/main.py, find this line:
   ```python
   model="llama3-8b-8192"
   ```
4. Change the model name to whatever the Ministry's API uses
5. If they use a different provider (not Groq), change the client too

The knowledge base (ZED_KNOWLEDGE in main.py) stays the same — that's what you control.

---

## Common problems and fixes

**"python is not recognized" error**
→ Python wasn't added to PATH during install. Reinstall Python and check the "Add to PATH" box.

**"ModuleNotFoundError" when running uvicorn**
→ You're not in the venv. Run the activate command from Step 3c again.

**Chatbot loads but shows "offline"**
→ Backend isn't running. Open a new terminal and run Step 5 again.

**"groq.AuthenticationError"**
→ Your API key is wrong. Double check .env file — no spaces around the = sign.

**Render deploy fails**
→ Check that Root Directory is set to "backend" in Render settings.

**Language dropdown shows English response when Hindi selected**
→ Normal on first message. Send one message first, then switch language.

---

## What to show in the POC demo (for JS level officers)

Suggested demo flow (10 minutes):

1. Open the chatbot URL
2. Ask: "What is ZED certification?" — shows basic knowledge
3. Ask: "I am a micro textile enterprise. How do I get Bronze?" — shows sector + persona awareness
4. Ask: "I have ISO 9001. Does it help?" — shows depth of knowledge
5. Ask: "How much subsidy will I get?" — shows subsidy calculation
6. Switch language to Hindi, ask: "ZED pledge kya hai?" — shows multilingual
7. Show the question_bank.json — explain this is 50 questions, all tested

Then explain what can be built next:
- Connect to actual PDF documents (RAG)
- WhatsApp bot using same backend
- IVR phone line using text-to-speech
- Dashboard for officers to see common questions

---

## Files you should NEVER share publicly

- backend/.env  (has your API key)
- That's it. Everything else is safe to share.

---

## Need help?

If something breaks, look at the terminal where uvicorn is running.
The error message there will tell you exactly what went wrong.

Most common fix: make sure (venv) is showing in your terminal before running anything.
