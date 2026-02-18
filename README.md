<div align="center">

<img src="https://img.icons8.com/fluency/96/artificial-intelligence.png" alt="logo" width="80"/>

# ✨ VidAI Studio

### Turn Any Video Into Content — Or Download It Instantly

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0+-000?style=flat-square&logo=flask)](https://flask.palletsprojects.com)
[![Gemini](https://img.shields.io/badge/Google_Gemini-API-4285F4?style=flat-square&logo=google&logoColor=white)](https://aistudio.google.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

<br/>

<img src="https://img.shields.io/badge/Facebook-supported-1877F2?style=for-the-badge&logo=facebook&logoColor=white" height="25"/>
<img src="https://img.shields.io/badge/YouTube-supported-FF0000?style=for-the-badge&logo=youtube&logoColor=white" height="25"/>
<img src="https://img.shields.io/badge/Instagram-supported-E4405F?style=for-the-badge&logo=instagram&logoColor=white" height="25"/>
<img src="https://img.shields.io/badge/TikTok-supported-000000?style=for-the-badge&logo=tiktok&logoColor=white" height="25"/>

</div>

---

## 🤔 What Is This?

**VidAI Studio** is a free, open-source desktop tool that does **two things**:

1. 🎥 **Download** any video (MP4) or audio (MP3) from Facebook, YouTube, Instagram, TikTok, and more
2. 🤖 **Generate AI content** from any video — summaries, articles, transcripts, or social posts — using Google Gemini

Just paste a link, click a button, and you're done. That's it. No complex setup, no paid software.

---

## 🚀 What Can It Do?

| Feature | What It Does |
|---|---|
| 📥 **Download Video** | Save any video as MP4 — one click, no AI needed |
| 🎵 **Download Audio** | Extract audio as MP3 (192kbps) — perfect for podcasts |
| 📝 **AI Summary** | Get a clean summary of what's said in the video |
| 📰 **AI Article** | Turn a video into a full blog-style article |
| 📄 **AI Transcript** | Get a written transcript of the video audio |
| 💬 **AI Social Post** | Generate a ready-to-post social media caption |
| 🌍 **6 Languages** | Bengali · English · Hindi · Arabic · Urdu · Spanish |
| 🤖 **4 AI Models** | Choose between Gemini 2.0 Flash, Flash Lite, 1.5 Flash, or 1.5 Pro |
| 🌙 **Dark Mode** | Easy on the eyes — toggles automatically or manually |
| 📊 **Live Progress** | See exactly what's happening: Download → Upload → Analyze → Done |
| 📜 **History** | Your past results are saved — reload anytime |
| 📤 **Export** | Download your AI result as `.md` or `.txt` |

---

## 📋 Before You Start

You need **3 things** installed on your computer:

| # | What | Where to Get It |
|---|---|---|
| 1️⃣ | **Python 3.9+** | [python.org/downloads](https://python.org/downloads) |
| 2️⃣ | **ffmpeg** | [ffmpeg.org/download](https://ffmpeg.org/download.html) |
| 3️⃣ | **Gemini API Key** *(free)* | [aistudio.google.com/apikey](https://aistudio.google.com/app/apikey) |

> 💡 **Don't have ffmpeg?**
> - **Windows:** Download from the link above, extract, and add the `bin` folder to your system PATH
> - **Mac:** Run `brew install ffmpeg` in Terminal  
> - **Linux:** Run `sudo apt install ffmpeg`

> 💡 **Getting a Gemini API Key is free!** Just go to [Google AI Studio](https://aistudio.google.com/app/apikey), sign in with Google, and click "Create API Key".

---

## ⚡ Setup (5 Minutes)

**Step 1 — Download the project**
```bash
git clone https://github.com/zihaaaad/vidai-studio.git
cd vidai-studio
```

**Step 2 — Create a virtual environment**
```bash
python3 -m venv venv

# Activate it:
source venv/bin/activate        # Mac / Linux
venv\Scripts\activate           # Windows
```

**Step 3 — Install dependencies**
```bash
pip install -r requirements.txt
```

**Step 4 — Run the app**
```bash
python app.py
```

🎉 **That's it!** The app opens in your browser at `http://127.0.0.1:5000`

---

## 🖥️ How to Use

### 🎥 Download a Video or Audio
> No AI key needed for this!

1. **Paste** a video URL into the input box
2. Click **`Video MP4`** or **`Audio MP3`** at the bottom of the sidebar
3. Wait for the progress bar to finish
4. ✅ The file downloads to your computer automatically

### 🤖 Generate AI Content
> Requires a Gemini API key (free)

1. Click the **⚙️ gear icon** and paste your API key *(only needed once)*
2. **Paste** a video URL
3. **Choose** your AI model, language, and output style
4. Click **`Generate Content`** *(or press `Ctrl + Enter`)*
5. Wait for the AI to analyze and write
6. ✅ **Copy**, **export as .md**, or **export as .txt**

---

## 📁 Project Structure

```
vidai-studio/
├── app.py                 # Backend — Flask server + AI logic
├── templates/
│   └── index.html         # Frontend — everything in one file
├── requirements.txt       # Python packages needed
├── config.json            # Created automatically — your API key
├── history.json           # Created automatically — past results
├── tmp/                   # Temp files — cleaned automatically
├── .gitignore
├── LICENSE
└── README.md
```

---

## 🏗️ Build as Windows EXE

Want to share it as a standalone `.exe`?

```bash
pip install pyinstaller
pyinstaller --onefile --add-data "templates:templates" app.py
```

> ⚠️ Put `ffmpeg.exe` next to the generated `.exe` file.

---

## 🔒 Your Data Is Safe

- Your API key stays **on your computer** in `config.json`
- It's only sent to Google's Gemini API — nowhere else
- **No tracking, no analytics, no third-party servers**

---

## 👨‍💻 Made By

<div align="center">

**Zihad Hasan**

*Assistant Trainer of Generative AI Tools*  
**As-Sunnah Skill Development Institute**

📧 [zihad.connects@gmail.com](mailto:zihad.connects@gmail.com)

[![Facebook](https://img.shields.io/badge/Facebook-1877F2?style=flat-square&logo=facebook&logoColor=white)](https://www.facebook.com/pkmzihad10)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/pkmzihad/)
[![X](https://img.shields.io/badge/X-000000?style=flat-square&logo=x&logoColor=white)](https://x.com/pkmzihad)

</div>

---

## 📄 License

Open source under the [MIT License](LICENSE) — use it, modify it, share it.

---

<div align="center">

**⭐ If you find this useful, give it a star!**

**Brainstorming with AI**

</div>
