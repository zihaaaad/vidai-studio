<div align="center">

<img src="https://img.icons8.com/fluency/96/artificial-intelligence.png" alt="logo" width="80"/>

# ✨ VidAI Studio

**Transform any video into professional content with AI — in seconds.**

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0+-000?style=flat-square&logo=flask)](https://flask.palletsprojects.com)
[![Gemini](https://img.shields.io/badge/Google_Gemini-API-4285F4?style=flat-square&logo=google&logoColor=white)](https://aistudio.google.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

<br/>

<img src="https://img.shields.io/badge/Facebook-supported-1877F2?style=for-the-badge&logo=facebook&logoColor=white" height="25"/>
<img src="https://img.shields.io/badge/YouTube-supported-FF0000?style=for-the-badge&logo=youtube&logoColor=white" height="25"/>
<img src="https://img.shields.io/badge/Instagram-supported-E4405F?style=for-the-badge&logo=instagram&logoColor=white" height="25"/>
<img src="https://img.shields.io/badge/TikTok-supported-000000?style=for-the-badge&logo=tiktok&logoColor=white" height="25"/>

---

*Paste a video link → choose your style → get AI-generated content instantly.*  
*Summaries, articles, transcripts, social posts — in 6 languages.*

</div>

<br/>

## 🚀 Features

| Feature | Description |
|---|---|
| 🎬 **Multi-Platform** | Facebook, YouTube, Instagram, TikTok, Twitter/X |
| 📝 **4 Output Styles** | Summary · Article · Transcript · Social Post |
| 🌍 **6 Languages** | Bengali · English · Hindi · Arabic · Urdu · Spanish |
| 🤖 **4 AI Models** | Gemini 2.0 Flash, Flash Lite, 1.5 Flash, 1.5 Pro |
| 🌙 **Dark Mode** | Auto-detects system preference with manual toggle |
| 📊 **Live Progress** | Real-time step-by-step processing updates |
| 📜 **History** | Auto-saved results — reload any past generation |
| 📥 **Export** | Download as `.md` or `.txt` |
| ✍️ **Custom Instructions** | Guide the AI with your own prompts |
| ⌨️ **Keyboard Shortcut** | `Ctrl + Enter` to generate instantly |

<br/>

## 📋 Requirements

Before you start, make sure you have:

- **Python 3.9** or higher → [Download](https://python.org)
- **ffmpeg** installed and in your PATH → [Download](https://ffmpeg.org/download.html)
- A free **Google Gemini API Key** → [Get one here](https://aistudio.google.com/app/apikey)

<br/>

## ⚡ Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/Z-root-X/vidai-studio.git
cd vidai-studio

# 2. Create a virtual environment
python3 -m venv venv
source venv/bin/activate        # Linux / macOS
# venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python app.py
```

🎉 The app will open automatically in your browser at **http://127.0.0.1:5000**

> On first launch, click the ⚙️ gear icon and paste your Gemini API key.

<br/>

## 🖥️ How to Use

1. **Paste** any video URL (Facebook, YouTube, Instagram, TikTok, etc.)
2. **Select** your preferred AI model, language, and output style
3. **Click** "Generate Content" (or press `Ctrl + Enter`)
4. **Watch** the live progress: Download → Upload → Analyze → Done
5. **Copy** or **export** your result as `.md` or `.txt`

<br/>

## 📁 Project Structure

```
vidai-studio/
├── app.py                 # Backend — Flask server + Gemini AI logic
├── templates/
│   └── index.html         # Frontend — Single-page application
├── requirements.txt       # Python dependencies
├── config.json            # Auto-created — stores your API key locally
├── history.json           # Auto-created — processing history
├── tmp/                   # Temporary audio files (auto-cleaned)
├── .gitignore
└── README.md
```

<br/>

## 🏗️ Build for Windows

```bash
pip install pyinstaller
pyinstaller --onefile --add-data "templates:templates" app.py
```

> **Note:** Place `ffmpeg.exe` in the same folder as the `.exe` file.

<br/>

## 🔒 Privacy

Your API key is stored **locally** in `config.json` — it is never sent anywhere except directly to Google's Gemini API. No telemetry, no tracking, no third-party servers.

<br/>

## 👨‍💻 Author

<div align="center">

**Zihad Hasan**

*Assistant Trainer of Generative AI Tools*  
**As-Sunnah Skill Development Institute**

📧 [zihad.connects@gmail.com](mailto:zihad.connects@gmail.com)

</div>

<br/>

## 📄 License

This project is licensed under the [MIT License](LICENSE).

<br/>

---

<div align="center">

Made with ❤️ and AI

</div>
